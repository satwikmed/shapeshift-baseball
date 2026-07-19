"""Secondary outcome labels used in intervention evaluation."""

from __future__ import annotations

import pandas as pd

CALLED_STRIKE_DESCRIPTIONS = frozenset({"called_strike"})
WHIFF_DESCRIPTIONS = frozenset({"swinging_strike", "swinging_strike_blocked", "missed_bunt"})
IN_ZONE_CODES = frozenset(range(1, 10))
HARD_CONTACT_LAUNCH = 95.0


def add_outcome_labels(frame: pd.DataFrame) -> pd.DataFrame:
    """Attach decision-quality and contact labels without replacing primary run value.

    These labels support secondary reporting for zone-strike quality, CSW, and hard
    contact. They are never used to detect interventions.
    """
    result = frame.copy()
    description = result["description"].astype("string") if "description" in result else pd.Series(
        pd.NA, index=result.index, dtype="string"
    )
    zone = pd.to_numeric(
        result["zone"] if "zone" in result else pd.Series(pd.NA, index=result.index),
        errors="coerce",
    )

    result["is_called_strike"] = description.isin(CALLED_STRIKE_DESCRIPTIONS).astype("int8")
    result["is_whiff"] = description.isin(WHIFF_DESCRIPTIONS).astype("int8")
    result["is_csw"] = (result["is_called_strike"] | result["is_whiff"]).astype("int8")
    result["is_in_zone"] = zone.isin(IN_ZONE_CODES).astype("int8")
    result["is_in_zone_miss"] = (result["is_in_zone"] & result["is_whiff"]).astype("int8")

    if "launch_speed" in result.columns:
        launch = pd.to_numeric(result["launch_speed"], errors="coerce")
        result["is_hard_contact"] = (launch >= HARD_CONTACT_LAUNCH).astype("Int8")
    else:
        result["is_hard_contact"] = pd.Series(pd.NA, index=result.index, dtype="Int8")

    return result
