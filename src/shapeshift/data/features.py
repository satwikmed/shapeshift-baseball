"""Leakage-aware physical pitch features."""

from __future__ import annotations

import numpy as np
import pandas as pd

from shapeshift.data.schema import PITCH_FAMILY, coerce_source_types

FEET_TO_INCHES = 12.0


def add_canonical_pitch_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Standardize handedness and movement from the pitcher's perspective.

    Prefer Savant's `api_break_x_arm` when present: it is already arm-side signed.
    Fallback reconstructs arm-side break from catcher-view `pfx_x` so positive values
    always mean arm-side movement for both handedness groups.
    """
    result = coerce_source_types(frame)
    hand_multiplier = np.where(result["p_throws"].eq("L"), -1.0, 1.0)

    result["pitch_family"] = result["pitch_type"].map(PITCH_FAMILY).fillna("other")
    if "api_break_x_arm" in result.columns:
        api_break = pd.to_numeric(result["api_break_x_arm"], errors="coerce")
        fallback = -result["pfx_x"] * hand_multiplier
        result["arm_side_break"] = api_break.fillna(fallback) * FEET_TO_INCHES
        result["arm_side_break_source"] = np.where(api_break.notna(), "api_break_x_arm", "pfx_x")
    else:
        result["arm_side_break"] = -result["pfx_x"] * FEET_TO_INCHES * hand_multiplier
        result["arm_side_break_source"] = "pfx_x"

    result["induced_vertical_break"] = result["pfx_z"] * FEET_TO_INCHES
    result["release_side"] = result["release_pos_x"] * hand_multiplier
    if "arm_angle" in result.columns:
        result["arm_angle"] = pd.to_numeric(result["arm_angle"], errors="coerce")

    if "delta_pitcher_run_exp" in result.columns:
        pitcher_re = pd.to_numeric(result["delta_pitcher_run_exp"], errors="coerce")
        result["pitcher_run_value"] = pitcher_re.fillna(-result["delta_run_exp"])
    else:
        result["pitcher_run_value"] = -result["delta_run_exp"]

    result["is_same_side"] = result["p_throws"].eq(result["stand"]).astype("int8")
    if "game_type" in result.columns:
        result["game_type"] = result["game_type"].astype("string").str.upper()
        result["is_regular_season"] = result["game_type"].eq("R")
    else:
        result["is_regular_season"] = True

    result["pitch_uid"] = (
        result["game_pk"].astype("Int64").astype("string")
        + "-"
        + result["at_bat_number"].astype("Int64").astype("string")
        + "-"
        + result["pitch_number"].astype("Int64").astype("string")
    )
    return result


def flag_quality_issues(frame: pd.DataFrame) -> pd.DataFrame:
    """Attach row-level, non-destructive quality flags."""
    result = frame.copy()
    result["qa_missing_identity"] = result[
        ["game_date", "game_pk", "pitcher", "pitch_type"]
    ].isna().any(axis=1)
    result["qa_missing_shape"] = result[
        ["release_speed", "pfx_x", "pfx_z", "release_pos_x", "release_pos_z"]
    ].isna().any(axis=1)
    result["qa_implausible_velocity"] = ~result["release_speed"].between(45, 110)
    result["qa_implausible_movement"] = (
        result["arm_side_break"].abs().gt(35)
        | result["induced_vertical_break"].abs().gt(35)
    )
    result["qa_non_regular_season"] = ~result["is_regular_season"].fillna(False)
    result["qa_exclude_primary"] = result[
        [
            "qa_missing_identity",
            "qa_missing_shape",
            "qa_implausible_velocity",
            "qa_implausible_movement",
            "qa_non_regular_season",
        ]
    ].any(axis=1)
    return result
