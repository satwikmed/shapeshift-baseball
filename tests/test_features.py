from __future__ import annotations

import pandas as pd
import pytest

from shapeshift.data.features import add_canonical_pitch_features, flag_quality_issues


def sample_pitches() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "game_date": ["2025-04-01", "2025-04-01"],
            "game_pk": [1, 1],
            "at_bat_number": [1, 1],
            "pitch_number": [1, 2],
            "pitcher": [10, 11],
            "player_name": ["Right, Pitcher", "Left, Pitcher"],
            "p_throws": ["R", "L"],
            "stand": ["R", "R"],
            "pitch_type": ["FF", "SL"],
            "release_speed": [95.0, 84.0],
            "release_spin_rate": [2300.0, 2500.0],
            "release_pos_x": [-2.0, 2.0],
            "release_pos_z": [6.0, 5.5],
            "release_extension": [6.5, 6.2],
            "pfx_x": [-0.8, 0.8],
            "pfx_z": [1.2, 0.2],
            "plate_x": [0.1, -0.2],
            "plate_z": [2.7, 2.3],
            "zone": [5, 6],
            "description": ["called_strike", "swinging_strike"],
            "events": [pd.NA, pd.NA],
            "delta_run_exp": [-0.03, -0.05],
            "game_type": ["R", "R"],
        }
    )


def test_horizontal_features_are_arm_side_positive() -> None:
    result = add_canonical_pitch_features(sample_pitches())

    # Catcher-view pfx_x of -0.8 for RHP and +0.8 for LHP are both arm-side.
    assert result["arm_side_break"].tolist() == pytest.approx([9.6, 9.6])
    assert result["release_side"].tolist() == [-2.0, -2.0]
    assert result["pitch_family"].tolist() == ["four_seam", "slider"]


def test_api_break_x_arm_is_preferred_when_present() -> None:
    frame = sample_pitches()
    frame["api_break_x_arm"] = [0.5, 0.25]
    result = add_canonical_pitch_features(frame)

    assert result["arm_side_break"].tolist() == pytest.approx([6.0, 3.0])
    assert result["arm_side_break_source"].tolist() == ["api_break_x_arm", "api_break_x_arm"]


def test_pitcher_run_value_prefers_pitcher_credited_column() -> None:
    frame = sample_pitches()
    frame["delta_pitcher_run_exp"] = [0.04, 0.06]
    result = add_canonical_pitch_features(frame)
    assert result["pitcher_run_value"].tolist() == [0.04, 0.06]


def test_quality_flags_preserve_rows() -> None:
    frame = sample_pitches()
    frame.loc[1, "release_speed"] = 130

    result = flag_quality_issues(add_canonical_pitch_features(frame))

    assert len(result) == 2
    assert result["qa_exclude_primary"].tolist() == [False, True]


def test_non_regular_season_rows_are_excluded() -> None:
    frame = sample_pitches()
    frame.loc[0, "game_type"] = "S"
    result = flag_quality_issues(add_canonical_pitch_features(frame))
    assert result["qa_exclude_primary"].tolist() == [True, False]
