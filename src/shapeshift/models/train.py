"""Train and persist a traceable shape-value model artifact."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import duckdb
import joblib
import pandas as pd

from shapeshift.config import Settings
from shapeshift.models.shape_value import (
    MODEL_FEATURES,
    evaluate_shape_value_model,
    fit_shape_value_model,
)
from shapeshift.models.temporal import TemporalBoundaries, assign_period


def load_model_frame(database: Path) -> pd.DataFrame:
    """Read only pre-committed model columns from validated storage."""
    columns = ["game_date", "qa_exclude_primary", "pitcher_run_value", *MODEL_FEATURES]
    select = ", ".join(columns)
    with duckdb.connect(str(database), read_only=True) as connection:
        return connection.execute(f"SELECT {select} FROM pitches").fetchdf()


def boundaries_from_settings(settings: Settings) -> TemporalBoundaries:
    data = settings.data
    return TemporalBoundaries(
        development_end=data.development_end,
        validation_start=data.validation_start,
        validation_end=data.validation_end,
        evaluation_start=data.evaluation_start,
        evaluation_end=data.evaluation_end,
        prospective_start=data.prospective_start,
    )


def train_and_validate(settings: Settings) -> dict[str, object]:
    """Train on development rows, score validation, and persist model plus metadata."""
    frame = load_model_frame(settings.paths.database)
    frame = frame.loc[~frame["qa_exclude_primary"]].copy()
    frame["game_date"] = pd.to_datetime(frame["game_date"], errors="coerce")
    frame = frame.loc[frame["game_date"].dt.date >= settings.data.start_date]
    frame["period"] = assign_period(frame["game_date"], boundaries_from_settings(settings))
    development = frame.loc[frame["period"].eq("development")]
    validation = frame.loc[frame["period"].eq("validation")]
    if development.empty or validation.empty:
        raise ValueError("Both development and validation periods need eligible pitches")

    model = fit_shape_value_model(
        development,
        random_seed=settings.project.random_seed,
    )
    scorecard = evaluate_shape_value_model(model, development, validation)

    model_directory = settings.paths.artifacts / "models"
    model_directory.mkdir(parents=True, exist_ok=True)
    model_path = model_directory / "shape_value.joblib"
    metadata_path = model_directory / "shape_value.metadata.json"
    joblib.dump(model, model_path)

    metadata: dict[str, object] = {
        "created_at_utc": datetime.now(UTC).isoformat(),
        "model_path": str(model_path),
        "features": list(MODEL_FEATURES),
        "development_rows": len(development),
        "validation_rows": len(validation),
        "development_last_date": str(development["game_date"].max()),
        "validation_first_date": str(validation["game_date"].min()),
        "validation_last_date": str(validation["game_date"].max()),
        "scorecard": scorecard.to_dict(),
    }
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return metadata
