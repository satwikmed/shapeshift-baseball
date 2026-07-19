from __future__ import annotations

from datetime import date

import pytest

from shapeshift.data.ingest import date_chunks


def test_date_chunks_are_inclusive_and_non_overlapping() -> None:
    chunks = list(date_chunks(date(2025, 4, 1), date(2025, 4, 10), 7))

    assert chunks == [
        (date(2025, 4, 1), date(2025, 4, 7)),
        (date(2025, 4, 8), date(2025, 4, 10)),
    ]


def test_date_chunks_reject_invalid_range() -> None:
    with pytest.raises(ValueError, match="end date"):
        list(date_chunks(date(2025, 4, 2), date(2025, 4, 1), 7))


def test_date_chunks_reject_non_positive_size() -> None:
    with pytest.raises(ValueError, match="positive"):
        list(date_chunks(date(2025, 4, 1), date(2025, 4, 2), 0))
