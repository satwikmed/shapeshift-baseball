"""Typed configuration loading."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ProjectConfig(StrictModel):
    name: str
    random_seed: int = 42


class PathConfig(StrictModel):
    raw: Path
    interim: Path
    processed: Path
    database: Path
    artifacts: Path


class DataConfig(StrictModel):
    source: str
    chunk_days: int = Field(ge=1, le=31)
    start_date: date
    historical_archive_start: date | None = None
    development_end: date
    validation_start: date
    validation_end: date
    evaluation_start: date
    evaluation_end: date
    prospective_start: date
    regular_season_only: bool = True


class InterventionConfig(StrictModel):
    pre_days: int = Field(gt=0)
    transition_days: int = Field(ge=0)
    post_days: int = Field(gt=0)
    min_pitches_each_side: int = Field(gt=0)
    min_games_each_side: int = Field(gt=0)
    persistence_share: float = Field(gt=0, le=1)
    rolling_window_pitches: int = Field(gt=10)


class ModelConfig(StrictModel):
    outcome_sign: str
    min_pitcher_pitch_count: int = Field(gt=0)
    calibration_bins: int = Field(gt=1)
    include_arm_angle: bool = True


class Settings(StrictModel):
    project: ProjectConfig
    paths: PathConfig
    data: DataConfig
    interventions: InterventionConfig
    model: ModelConfig


def load_settings(path: Path = Path("config/default.yaml")) -> Settings:
    """Load and validate a YAML configuration file."""
    with path.open(encoding="utf-8") as file:
        payload: Any = yaml.safe_load(file)
    return Settings.model_validate(payload)
