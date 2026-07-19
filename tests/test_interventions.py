from __future__ import annotations

import pandas as pd

from shapeshift.interventions.detect import (
    SHAPE_FEATURES,
    WindowSpec,
    add_robust_change_scores,
    build_window_comparisons,
)


def game_states() -> pd.DataFrame:
    dates = pd.date_range("2025-04-01", periods=12, freq="7D")
    rows: list[dict[str, object]] = []
    for pitcher, shift in [(1, 0.0), (2, 3.0), (3, -1.0)]:
        for index, game_date in enumerate(dates):
            value = 95.0 + (shift if index >= 6 else 0.0)
            row: dict[str, object] = {
                "pitcher": pitcher,
                "pitch_family": "four_seam",
                "game_date": game_date,
                "pitch_count": 20,
            }
            for feature in SHAPE_FEATURES:
                row[feature] = value
            rows.append(row)
    return pd.DataFrame(rows)


def test_window_comparisons_do_not_require_outcomes() -> None:
    comparisons = build_window_comparisons(
        game_states(),
        WindowSpec(
            pre_days=35,
            transition_days=0,
            post_days=35,
            min_pitches=60,
            min_games=3,
        ),
    )

    assert not comparisons.empty
    assert all("run_value" not in column for column in comparisons.columns)
    changed = comparisons.loc[comparisons["pitcher"].eq(2), "delta_release_speed"]
    assert changed.max() == 3.0


def test_robust_scores_rank_largest_change() -> None:
    comparisons = pd.DataFrame(
        {
            "pitch_family": ["four_seam"] * 5,
            **{
                f"delta_{feature}": [0.0, 0.1, -0.1, 0.2, 3.0]
                for feature in SHAPE_FEATURES
            },
        }
    )

    result = add_robust_change_scores(comparisons)

    assert result["max_abs_robust_z"].idxmax() == 4
    assert result.loc[4, "primary_change_feature"] in SHAPE_FEATURES
