"""Context-neutral physical pitch-value model and baseline scorecard."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, root_mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

NUMERIC_FEATURES = (
    "release_speed",
    "arm_side_break",
    "induced_vertical_break",
    "release_side",
    "release_pos_z",
    "release_extension",
    "release_spin_rate",
    "arm_angle",
)
CATEGORICAL_FEATURES = ("pitch_family", "p_throws", "stand")
MODEL_FEATURES = (*NUMERIC_FEATURES, *CATEGORICAL_FEATURES)
FORBIDDEN_FEATURES = frozenset(
    {
        "pitcher",
        "player_name",
        "plate_x",
        "plate_z",
        "zone",
        "balls",
        "strikes",
        "description",
        "events",
        "delta_run_exp",
        "pitcher_run_value",
    }
)


@dataclass(frozen=True)
class Scorecard:
    rows: int
    model_mae: float
    model_rmse: float
    baseline_mae: float
    baseline_rmse: float
    rmse_improvement_pct: float

    def to_dict(self) -> dict[str, int | float]:
        return asdict(self)


def assert_leakage_safe(features: tuple[str, ...]) -> None:
    """Reject identifiers, location, context, and post-pitch information."""
    leaked = sorted(set(features).intersection(FORBIDDEN_FEATURES))
    if leaked:
        raise ValueError(f"Forbidden shape-model features: {', '.join(leaked)}")


def build_shape_value_pipeline(random_seed: int = 42) -> Pipeline:
    """Construct a reproducible nonlinear baseline for physical pitch quality."""
    assert_leakage_safe(MODEL_FEATURES)
    numeric = Pipeline(
        [
            ("impute", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
        ]
    )
    categorical = Pipeline(
        [
            ("impute", SimpleImputer(strategy="most_frequent")),
            (
                "encode",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
            ),
        ]
    )
    preprocessor = ColumnTransformer(
        [
            ("numeric", numeric, list(NUMERIC_FEATURES)),
            ("categorical", categorical, list(CATEGORICAL_FEATURES)),
        ],
        verbose_feature_names_out=False,
    )
    regressor = HistGradientBoostingRegressor(
        loss="squared_error",
        learning_rate=0.06,
        max_iter=250,
        max_leaf_nodes=31,
        min_samples_leaf=100,
        l2_regularization=1.0,
        random_state=random_seed,
    )
    return Pipeline([("features", preprocessor), ("regressor", regressor)])


def fit_shape_value_model(
    training: pd.DataFrame,
    *,
    target: str = "pitcher_run_value",
    random_seed: int = 42,
) -> Pipeline:
    """Fit using only the pre-committed physical feature list."""
    missing = sorted(set((*MODEL_FEATURES, target)) - set(training.columns))
    if missing:
        raise ValueError(f"Training data is missing: {', '.join(missing)}")
    eligible = training[target].notna()
    model = build_shape_value_pipeline(random_seed)
    return model.fit(training.loc[eligible, list(MODEL_FEATURES)], training.loc[eligible, target])


def evaluate_shape_value_model(
    model: Any,
    training: pd.DataFrame,
    evaluation: pd.DataFrame,
    *,
    target: str = "pitcher_run_value",
) -> Scorecard:
    """Compare model predictions with a frozen pitch-family-mean baseline."""
    eligible = evaluation[target].notna()
    test = evaluation.loc[eligible]
    actual = test[target].to_numpy(dtype=float)
    predicted = np.asarray(model.predict(test.loc[:, list(MODEL_FEATURES)]), dtype=float)

    family_means = training.groupby("pitch_family", observed=True)[target].mean()
    global_mean = float(training[target].mean())
    baseline = test["pitch_family"].map(family_means).fillna(global_mean).to_numpy(dtype=float)

    model_rmse = float(root_mean_squared_error(actual, predicted))
    baseline_rmse = float(root_mean_squared_error(actual, baseline))
    improvement = 100 * (baseline_rmse - model_rmse) / baseline_rmse
    return Scorecard(
        rows=len(test),
        model_mae=float(mean_absolute_error(actual, predicted)),
        model_rmse=model_rmse,
        baseline_mae=float(mean_absolute_error(actual, baseline)),
        baseline_rmse=baseline_rmse,
        rmse_improvement_pct=float(improvement),
    )
