"""Detect persistent physical pitch changes without consulting outcomes."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

SHAPE_FEATURES = (
    "release_speed",
    "arm_side_break",
    "induced_vertical_break",
    "release_side",
    "release_pos_z",
    "release_extension",
    "release_spin_rate",
)


@dataclass(frozen=True)
class WindowSpec:
    pre_days: int = 60
    transition_days: int = 7
    post_days: int = 60
    min_pitches: int = 100
    min_games: int = 3


DEFAULT_WINDOW_SPEC = WindowSpec()


def aggregate_game_shapes(
    pitches: pd.DataFrame,
    features: tuple[str, ...] = SHAPE_FEATURES,
) -> pd.DataFrame:
    """Aggregate physical characteristics to pitcher-pitch-game states."""
    required = {"pitcher", "pitch_family", "game_date", *features}
    missing = sorted(required - set(pitches.columns))
    if missing:
        raise ValueError(f"Missing intervention columns: {', '.join(missing)}")

    excluded = (
        pitches["qa_exclude_primary"]
        if "qa_exclude_primary" in pitches
        else pd.Series(False, index=pitches.index)
    )
    clean = pitches.loc[~excluded].copy()
    clean["game_date"] = pd.to_datetime(clean["game_date"])
    games = (
        clean.groupby(["pitcher", "pitch_family", "game_date"], observed=True)
        .agg(
            **{feature: (feature, "mean") for feature in features},
            pitch_count=("game_date", "size"),
        )
        .reset_index()
        .sort_values(["pitcher", "pitch_family", "game_date"])
    )
    return games


def _weighted_means(window: pd.DataFrame, features: tuple[str, ...]) -> dict[str, float]:
    weights = window["pitch_count"].to_numpy(dtype=float)
    return {
        feature: float(np.average(window[feature].to_numpy(dtype=float), weights=weights))
        for feature in features
    }


def build_window_comparisons(
    game_shapes: pd.DataFrame,
    spec: WindowSpec = DEFAULT_WINDOW_SPEC,
    features: tuple[str, ...] = SHAPE_FEATURES,
    candidate_dates: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Compare pre/post physical states around every eligible game date.

    Dates in the transition buffer are excluded. No outcome column is accepted or used.
    Multiple adjacent candidate dates are intentionally retained here; a later
    persistence/consolidation stage selects one event from each change episode.
    """
    records: list[dict[str, object]] = []
    grouped = game_shapes.groupby(["pitcher", "pitch_family"], observed=True, sort=False)
    candidate_lookup: dict[tuple[object, object], set[pd.Timestamp]] | None = None
    if candidate_dates is not None and not candidate_dates.empty:
        candidate_lookup = {}
        for (pitcher, pitch_family), subset in candidate_dates.groupby(
            ["pitcher", "pitch_family"], observed=True
        ):
            candidate_lookup[(pitcher, pitch_family)] = {
                pd.Timestamp(value) for value in subset["game_date"]
            }

    for (pitcher, pitch_family), group in grouped:
        group = group.sort_values("game_date").reset_index(drop=True)
        dates = group["game_date"]
        if candidate_lookup is not None:
            allowed = candidate_lookup.get((pitcher, pitch_family), set())
            dates = [value for value in dates if pd.Timestamp(value) in allowed]
        for change_date in dates:
            pre_start = change_date - pd.Timedelta(days=spec.pre_days)
            pre_end = change_date - pd.Timedelta(days=spec.transition_days + 1)
            post_start = change_date + pd.Timedelta(days=spec.transition_days + 1)
            post_end = change_date + pd.Timedelta(days=spec.post_days)
            pre = group[group["game_date"].between(pre_start, pre_end)]
            post = group[group["game_date"].between(post_start, post_end)]
            pre_count = int(pre["pitch_count"].sum())
            post_count = int(post["pitch_count"].sum())
            if (
                pre_count < spec.min_pitches
                or post_count < spec.min_pitches
                or len(pre) < spec.min_games
                or len(post) < spec.min_games
            ):
                continue

            pre_means = _weighted_means(pre, features)
            post_means = _weighted_means(post, features)
            record: dict[str, object] = {
                "pitcher": pitcher,
                "pitch_family": pitch_family,
                "change_date": change_date,
                "pre_pitches": pre_count,
                "post_pitches": post_count,
                "pre_games": len(pre),
                "post_games": len(post),
            }
            for feature in features:
                record[f"pre_{feature}"] = pre_means[feature]
                record[f"post_{feature}"] = post_means[feature]
                record[f"delta_{feature}"] = post_means[feature] - pre_means[feature]
            records.append(record)
    return pd.DataFrame.from_records(records)


def add_robust_change_scores(
    comparisons: pd.DataFrame,
    features: tuple[str, ...] = SHAPE_FEATURES,
    *,
    minimum_scale: float = 1e-6,
) -> pd.DataFrame:
    """Scale changes by pitch-family median absolute deviation.

    This is a ranking primitive, not the final treatment rule. Thresholds must be frozen
    on the development period before the locked evaluation period is inspected.
    """
    result = comparisons.copy()
    score_columns: list[str] = []
    for feature in features:
        delta = f"delta_{feature}"
        score = f"robust_z_{feature}"
        grouped = result.groupby("pitch_family", observed=True)[delta]
        median = grouped.transform("median")
        mad = grouped.transform(lambda values: (values - values.median()).abs().median())
        scale = (1.4826 * mad).clip(lower=minimum_scale)
        result[score] = (result[delta] - median) / scale
        score_columns.append(score)
    result["max_abs_robust_z"] = result[score_columns].abs().max(axis=1)
    result["primary_change_feature"] = (
        result[score_columns].abs().idxmax(axis=1).str.removeprefix("robust_z_")
    )
    return result
