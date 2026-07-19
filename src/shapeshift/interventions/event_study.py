"""Matched event-study estimates for pitch-shape interventions."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd

MATCH_FEATURES = (
    "pre_release_speed",
    "pre_arm_side_break",
    "pre_induced_vertical_break",
    "pre_release_side",
    "pre_release_pos_z",
    "pre_release_extension",
    "pre_release_spin_rate",
    "pre_value_per_100",
)


@dataclass(frozen=True)
class EffectEstimate:
    n_treated: int
    n_matched: int
    ate_per_100: float
    ate_ci_low: float
    ate_ci_high: float
    treated_delta: float
    control_delta: float
    pretrend_gap: float
    positive_share: float

    def to_dict(self) -> dict[str, float | int]:
        return asdict(self)


def _standardize(frame: pd.DataFrame, columns: tuple[str, ...]) -> pd.DataFrame:
    result = frame.copy()
    for column in columns:
        values = result[column].astype(float)
        scale = values.std(ddof=0)
        if scale < 1e-8:
            result[column] = 0.0
        else:
            result[column] = (values - values.mean()) / scale
    return result


def match_controls(
    treated: pd.DataFrame,
    donor_pool: pd.DataFrame,
    *,
    caliper: float = 1.25,
    n_matches: int = 5,
) -> pd.DataFrame:
    """Nearest-neighbor match within pitch family using pre-period characteristics."""
    if treated.empty or donor_pool.empty:
        return pd.DataFrame()

    records: list[dict[str, object]] = []
    for pitch_family, treated_group in treated.groupby("pitch_family", observed=True):
        donors = donor_pool.loc[donor_pool["pitch_family"].eq(pitch_family)].copy()
        if donors.empty:
            continue
        feature_frame = pd.concat(
            [treated_group[list(MATCH_FEATURES)], donors[list(MATCH_FEATURES)]],
            ignore_index=True,
        )
        standardized = _standardize(feature_frame, MATCH_FEATURES)
        treated_matrix = standardized.iloc[: len(treated_group)].to_numpy(dtype=float)
        donor_matrix = standardized.iloc[len(treated_group) :].to_numpy(dtype=float)
        donor_index = donors.reset_index(drop=True)

        for row_idx, (_, treated_row) in enumerate(treated_group.iterrows()):
            distances = np.linalg.norm(donor_matrix - treated_matrix[row_idx], axis=1)
            order = np.argsort(distances)
            selected = 0
            for donor_pos in order:
                if distances[donor_pos] > caliper:
                    break
                donor = donor_index.iloc[int(donor_pos)]
                if donor["pitcher"] == treated_row["pitcher"]:
                    continue
                records.append(
                    {
                        "treated_pitcher": treated_row["pitcher"],
                        "treated_pitch_family": treated_row["pitch_family"],
                        "treated_change_date": treated_row["change_date"],
                        "control_pitcher": donor["pitcher"],
                        "control_pitch_family": donor["pitch_family"],
                        "control_change_date": donor["change_date"],
                        "match_distance": float(distances[donor_pos]),
                        "treated_delta": float(treated_row["delta_value_per_100"]),
                        "control_delta": float(donor["delta_value_per_100"]),
                        "treated_pretrend": float(treated_row.get("pretrend_delta", 0.0)),
                        "control_pretrend": float(donor.get("pretrend_delta", 0.0)),
                    }
                )
                selected += 1
                if selected >= n_matches:
                    break
    return pd.DataFrame.from_records(records)


def estimate_effect(matches: pd.DataFrame, *, n_bootstrap: int = 400) -> EffectEstimate:
    """Estimate matched average treatment effect with pitcher-clustered bootstrap."""
    if matches.empty:
        return EffectEstimate(
            n_treated=0,
            n_matched=0,
            ate_per_100=0.0,
            ate_ci_low=0.0,
            ate_ci_high=0.0,
            treated_delta=0.0,
            control_delta=0.0,
            pretrend_gap=0.0,
            positive_share=0.0,
        )

    pair_effect = matches["treated_delta"] - matches["control_delta"]
    treated_ids = matches["treated_pitcher"].unique()
    rng = np.random.default_rng(42)
    boot: list[float] = []
    for _ in range(n_bootstrap):
        sample_ids = rng.choice(treated_ids, size=len(treated_ids), replace=True)
        mask = matches["treated_pitcher"].isin(sample_ids)
        boot.append(float(pair_effect.loc[mask].mean()))
    boot_arr = np.asarray(boot, dtype=float)
    return EffectEstimate(
        n_treated=int(len(treated_ids)),
        n_matched=int(len(matches)),
        ate_per_100=float(pair_effect.mean()),
        ate_ci_low=float(np.quantile(boot_arr, 0.10)),
        ate_ci_high=float(np.quantile(boot_arr, 0.90)),
        treated_delta=float(matches["treated_delta"].mean()),
        control_delta=float(matches["control_delta"].mean()),
        pretrend_gap=float(
            (matches["treated_pretrend"] - matches["control_pretrend"]).mean()
        ),
        positive_share=float((pair_effect > 0).mean()),
    )
