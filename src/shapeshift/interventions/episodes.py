"""Consolidate candidate change dates into persistent intervention episodes."""

from __future__ import annotations

import pandas as pd


def consolidate_episodes(
    scored: pd.DataFrame,
    *,
    z_threshold: float,
    min_gap_days: int = 30,
) -> pd.DataFrame:
    """Keep local maxima of robust change scores above a frozen threshold."""
    if scored.empty:
        return scored.copy()

    eligible = scored.loc[scored["max_abs_robust_z"] >= z_threshold].copy()
    if eligible.empty:
        return eligible

    eligible = eligible.sort_values(
        ["pitcher", "pitch_family", "change_date", "max_abs_robust_z"],
        ascending=[True, True, True, False],
    )
    kept: list[pd.Series] = []
    for _, group in eligible.groupby(["pitcher", "pitch_family"], sort=False):
        last_date: pd.Timestamp | None = None
        for _, row in group.iterrows():
            change_date = pd.Timestamp(row["change_date"])
            if last_date is not None and (change_date - last_date).days < min_gap_days:
                continue
            kept.append(row)
            last_date = change_date
    if not kept:
        return eligible.iloc[0:0].copy()
    return pd.DataFrame(kept).reset_index(drop=True)


def freeze_threshold(
    validation_scored: pd.DataFrame,
    *,
    quantile: float = 0.90,
) -> float:
    """Freeze the robust-z threshold using the validation era only."""
    if validation_scored.empty:
        raise ValueError("Cannot freeze threshold on an empty validation set")
    return float(validation_scored["max_abs_robust_z"].quantile(quantile))
