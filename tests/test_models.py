from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from shapeshift.models.shape_value import (
    MODEL_FEATURES,
    assert_leakage_safe,
    evaluate_shape_value_model,
    fit_shape_value_model,
)


def model_frame(rows: int = 500) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    speed = rng.normal(93, 3, rows)
    run_value = 0.005 * (speed - 93) + rng.normal(0, 0.005, rows)
    return pd.DataFrame(
        {
            "release_speed": speed,
            "arm_side_break": rng.normal(8, 3, rows),
            "induced_vertical_break": rng.normal(15, 3, rows),
            "release_side": rng.normal(-2, 0.3, rows),
            "release_pos_z": rng.normal(5.8, 0.3, rows),
            "release_extension": rng.normal(6.4, 0.3, rows),
            "release_spin_rate": rng.normal(2300, 150, rows),
            "arm_angle": rng.normal(40, 8, rows),
            "pitch_family": np.where(speed > 92, "four_seam", "slider"),
            "p_throws": "R",
            "stand": np.where(rng.random(rows) > 0.5, "R", "L"),
            "pitcher_run_value": run_value,
        }
    )


def test_shape_model_feature_contract_is_leakage_safe() -> None:
    assert_leakage_safe(MODEL_FEATURES)
    with pytest.raises(ValueError, match="plate_x"):
        assert_leakage_safe((*MODEL_FEATURES, "plate_x"))


def test_shape_model_beats_family_mean_on_known_signal() -> None:
    training = model_frame(500)
    evaluation = model_frame(250)
    model = fit_shape_value_model(training)

    scorecard = evaluate_shape_value_model(model, training, evaluation)

    assert scorecard.rows == 250
    assert scorecard.model_rmse < scorecard.baseline_rmse
