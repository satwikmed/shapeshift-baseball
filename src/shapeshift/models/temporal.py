"""Locked temporal partitions for honest model evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import pandas as pd


@dataclass(frozen=True)
class TemporalBoundaries:
    development_end: date
    validation_start: date
    validation_end: date
    evaluation_start: date
    evaluation_end: date
    prospective_start: date

    def __post_init__(self) -> None:
        ordered = (
            self.development_end,
            self.validation_start,
            self.validation_end,
            self.evaluation_start,
            self.evaluation_end,
            self.prospective_start,
        )
        if list(ordered) != sorted(ordered):
            raise ValueError("Temporal boundaries must be ordered")


def assign_period(dates: pd.Series, boundaries: TemporalBoundaries) -> pd.Series:
    """Assign periods without allowing locked evaluation rows into development."""
    parsed = pd.to_datetime(dates, errors="coerce")
    result = pd.Series("unassigned", index=dates.index, dtype="string")
    result.loc[parsed.dt.date <= boundaries.development_end] = "development"
    result.loc[
        parsed.dt.date.between(boundaries.validation_start, boundaries.validation_end)
    ] = "validation"
    result.loc[
        parsed.dt.date.between(boundaries.evaluation_start, boundaries.evaluation_end)
    ] = "evaluation"
    result.loc[parsed.dt.date >= boundaries.prospective_start] = "prospective"
    result.loc[parsed.isna()] = "invalid"
    return result
