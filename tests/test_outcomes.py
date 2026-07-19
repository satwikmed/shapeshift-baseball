from __future__ import annotations

import pandas as pd

from shapeshift.data.outcomes import add_outcome_labels


def sample_outcomes() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "description": [
                "called_strike",
                "swinging_strike",
                "ball",
                "hit_into_play",
            ],
            "zone": [5, 5, 13, 6],
            "launch_speed": [pd.NA, pd.NA, pd.NA, 101.0],
        }
    )


def test_outcome_labels_mark_csw_and_zone_misses() -> None:
    result = add_outcome_labels(sample_outcomes())

    assert result["is_csw"].tolist() == [1, 1, 0, 0]
    assert result["is_in_zone"].tolist() == [1, 1, 0, 1]
    assert result["is_in_zone_miss"].tolist() == [0, 1, 0, 0]
    assert result["is_hard_contact"].tolist()[3] == 1
