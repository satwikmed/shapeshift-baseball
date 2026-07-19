from __future__ import annotations

from datetime import date

import pandas as pd
import pytest

from shapeshift.models.temporal import TemporalBoundaries, assign_period


def boundaries() -> TemporalBoundaries:
    return TemporalBoundaries(
        development_end=date(2023, 11, 30),
        validation_start=date(2024, 3, 20),
        validation_end=date(2024, 11, 30),
        evaluation_start=date(2025, 3, 20),
        evaluation_end=date(2025, 11, 30),
        prospective_start=date(2026, 3, 20),
    )


def test_assign_period_preserves_temporal_gaps() -> None:
    dates = pd.Series(
        [
            "2023-11-30",
            "2024-01-01",
            "2024-03-20",
            "2025-03-20",
            "2026-03-20",
            None,
        ]
    )

    assert assign_period(dates, boundaries()).tolist() == [
        "development",
        "unassigned",
        "validation",
        "evaluation",
        "prospective",
        "invalid",
    ]


def test_boundaries_must_be_ordered() -> None:
    with pytest.raises(ValueError, match="ordered"):
        TemporalBoundaries(
            development_end=date(2025, 1, 1),
            validation_start=date(2024, 1, 1),
            validation_end=date(2024, 2, 1),
            evaluation_start=date(2025, 3, 1),
            evaluation_end=date(2025, 4, 1),
            prospective_start=date(2026, 1, 1),
        )
