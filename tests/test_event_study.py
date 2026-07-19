from __future__ import annotations

import pandas as pd

from shapeshift.interventions.episodes import consolidate_episodes, freeze_threshold
from shapeshift.interventions.event_study import estimate_effect, match_controls


def test_freeze_threshold_uses_validation_quantile() -> None:
    frame = pd.DataFrame({"max_abs_robust_z": [1.0, 2.0, 3.0, 4.0]})
    assert freeze_threshold(frame, quantile=0.75) == 3.25


def test_consolidate_episodes_enforces_gap() -> None:
    frame = pd.DataFrame(
        {
            "pitcher": [1, 1, 1],
            "pitch_family": ["slider", "slider", "slider"],
            "change_date": pd.to_datetime(["2025-05-01", "2025-05-10", "2025-07-01"]),
            "max_abs_robust_z": [3.0, 4.0, 3.5],
        }
    )
    result = consolidate_episodes(frame, z_threshold=2.5, min_gap_days=30)
    assert len(result) == 2
    assert result["change_date"].tolist() == list(pd.to_datetime(["2025-05-01", "2025-07-01"]))


def test_match_and_effect_are_finite() -> None:
    treated = pd.DataFrame(
        {
            "pitcher": [1],
            "pitch_family": ["slider"],
            "change_date": pd.to_datetime(["2025-06-01"]),
            "pre_release_speed": [85.0],
            "pre_arm_side_break": [8.0],
            "pre_induced_vertical_break": [2.0],
            "pre_release_side": [-1.8],
            "pre_release_pos_z": [5.8],
            "pre_release_extension": [6.4],
            "pre_release_spin_rate": [2400.0],
            "pre_value_per_100": [0.1],
            "delta_value_per_100": [0.8],
            "pretrend_delta": [0.05],
        }
    )
    donors = treated.copy()
    donors["pitcher"] = [2, 3, 4, 5, 6][:1]
    donors = pd.concat([donors.assign(pitcher=i, delta_value_per_100=0.1) for i in range(2, 8)])
    matches = match_controls(treated, donors, caliper=5.0, n_matches=3)
    effect = estimate_effect(matches, n_bootstrap=50)
    assert effect.n_treated == 1
    assert effect.ate_per_100 > 0
