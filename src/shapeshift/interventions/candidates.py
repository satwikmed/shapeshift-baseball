"""Candidate date thinning for scalable intervention detection."""

from __future__ import annotations

import pandas as pd


def thin_candidate_dates(game_shapes: pd.DataFrame, *, stride_games: int = 3) -> pd.DataFrame:
    """Evaluate pre/post windows on every Nth appearance to keep detection tractable."""
    if stride_games < 1:
        raise ValueError("stride_games must be positive")
    frames: list[pd.DataFrame] = []
    for _, group in game_shapes.groupby(["pitcher", "pitch_family"], sort=False):
        ordered = group.sort_values("game_date").reset_index(drop=True)
        # Keep enough interior dates for pre/post support.
        if len(ordered) < 8:
            continue
        candidates = ordered.iloc[3:-3:stride_games]
        frames.append(candidates)
    if not frames:
        return game_shapes.iloc[0:0].copy()
    return pd.concat(frames, ignore_index=True)
