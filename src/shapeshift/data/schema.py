"""Statcast input contract and canonical pitch mappings."""

from __future__ import annotations

from collections.abc import Iterable

import pandas as pd

REQUIRED_COLUMNS = frozenset(
    {
        "game_date",
        "game_pk",
        "at_bat_number",
        "pitch_number",
        "pitcher",
        "player_name",
        "p_throws",
        "stand",
        "pitch_type",
        "release_speed",
        "release_spin_rate",
        "release_pos_x",
        "release_pos_z",
        "release_extension",
        "pfx_x",
        "pfx_z",
        "plate_x",
        "plate_z",
        "zone",
        "description",
        "events",
        "delta_run_exp",
    }
)

OPTIONAL_COLUMNS = frozenset(
    {
        "game_type",
        "arm_angle",
        "api_break_x_arm",
        "api_break_z_with_gravity",
        "delta_pitcher_run_exp",
        "effective_speed",
        "launch_speed",
        "launch_angle",
    }
)

NUMERIC_COLUMNS = frozenset(
    {
        "game_pk",
        "at_bat_number",
        "pitch_number",
        "pitcher",
        "release_speed",
        "release_spin_rate",
        "release_pos_x",
        "release_pos_z",
        "release_extension",
        "pfx_x",
        "pfx_z",
        "plate_x",
        "plate_z",
        "zone",
        "delta_run_exp",
        "arm_angle",
        "api_break_x_arm",
        "api_break_z_with_gravity",
        "delta_pitcher_run_exp",
        "effective_speed",
        "launch_speed",
        "launch_angle",
    }
)

PITCH_FAMILY = {
    "FF": "four_seam",
    "FA": "four_seam",
    "SI": "sinker",
    "FT": "sinker",
    "FC": "cutter",
    "SL": "slider",
    "ST": "sweeper",
    "SV": "slurve",
    "CU": "curveball",
    "KC": "curveball",
    "CS": "curveball",
    "CH": "changeup",
    "FS": "splitter",
    "FO": "splitter",
    "SC": "screwball",
    "KN": "knuckleball",
}


class SchemaError(ValueError):
    """Raised when Statcast input violates the data contract."""


def validate_columns(frame: pd.DataFrame, required: Iterable[str] = REQUIRED_COLUMNS) -> None:
    """Raise a useful error when required source columns are absent."""
    if frame.empty:
        return
    missing = sorted(set(required) - set(frame.columns))
    if missing:
        raise SchemaError(f"Statcast extract is missing required columns: {', '.join(missing)}")


def coerce_source_types(frame: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with deterministic source types."""
    validate_columns(frame)
    result = frame.copy()
    result["game_date"] = pd.to_datetime(result["game_date"], errors="coerce")
    for column in NUMERIC_COLUMNS.intersection(result.columns):
        result[column] = pd.to_numeric(result[column], errors="coerce")
    for column in ("p_throws", "stand", "pitch_type"):
        result[column] = result[column].astype("string").str.upper()
    return result
