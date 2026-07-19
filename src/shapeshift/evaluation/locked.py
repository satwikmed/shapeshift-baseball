"""Locked ShapeShift evaluation: train, detect, match, and report."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import duckdb
import joblib
import numpy as np
import pandas as pd

from shapeshift.config import Settings, load_settings
from shapeshift.interventions.candidates import thin_candidate_dates
from shapeshift.interventions.detect import (
    SHAPE_FEATURES,
    WindowSpec,
    add_robust_change_scores,
    aggregate_game_shapes,
    build_window_comparisons,
)
from shapeshift.interventions.episodes import consolidate_episodes, freeze_threshold
from shapeshift.interventions.event_study import estimate_effect, match_controls
from shapeshift.models.shape_value import MODEL_FEATURES, fit_shape_value_model
from shapeshift.models.temporal import assign_period
from shapeshift.models.train import boundaries_from_settings


def _load_pitch_frame(database: Path) -> pd.DataFrame:
    columns = [
        "game_date",
        "pitcher",
        "player_name",
        "p_throws",
        "pitch_family",
        "qa_exclude_primary",
        "pitcher_run_value",
        "is_csw",
        "is_in_zone",
        *SHAPE_FEATURES,
        *MODEL_FEATURES,
    ]
    # MODEL_FEATURES overlaps SHAPE_FEATURES partially; unique preserve order.
    ordered = list(dict.fromkeys(columns))
    select = ", ".join(ordered)
    with duckdb.connect(str(database), read_only=True) as connection:
        frame = connection.execute(f"SELECT {select} FROM pitches").fetchdf()
    frame["game_date"] = pd.to_datetime(frame["game_date"], errors="coerce")
    return frame.loc[~frame["qa_exclude_primary"]].copy()


def _attach_predictions(frame: pd.DataFrame, model: Any) -> pd.DataFrame:
    result = frame.copy()
    predicted = np.asarray(model.predict(result.loc[:, list(MODEL_FEATURES)]), dtype=float)
    result["predicted_value"] = predicted
    result["predicted_value_per_100"] = predicted * 100.0
    return result


def _game_values(frame: pd.DataFrame) -> pd.DataFrame:
    return (
        frame.groupby(["pitcher", "pitch_family", "game_date"], observed=True)
        .agg(
            value_per_100=("predicted_value_per_100", "mean"),
            observed_per_100=("pitcher_run_value", lambda s: float(s.mean() * 100.0)),
            csw_rate=("is_csw", "mean"),
            in_zone_rate=("is_in_zone", "mean"),
            pitch_count=("predicted_value_per_100", "size"),
            player_name=("player_name", "first"),
            p_throws=("p_throws", "first"),
        )
        .reset_index()
    )


def _window_outcome_deltas(
    game_values: pd.DataFrame,
    interventions: pd.DataFrame,
    *,
    pre_days: int,
    transition_days: int,
    post_days: int,
) -> pd.DataFrame:
    records: list[dict[str, object]] = []
    grouped = game_values.groupby(["pitcher", "pitch_family"], observed=True, sort=False)
    lookup = {key: group.sort_values("game_date") for key, group in grouped}
    for _, event in interventions.iterrows():
        key = (event["pitcher"], event["pitch_family"])
        group = lookup.get(key)
        if group is None:
            continue
        change_date = pd.Timestamp(event["change_date"])
        pre_start = change_date - pd.Timedelta(days=pre_days)
        pre_end = change_date - pd.Timedelta(days=transition_days + 1)
        post_start = change_date + pd.Timedelta(days=transition_days + 1)
        post_end = change_date + pd.Timedelta(days=post_days)
        pre = group[group["game_date"].between(pre_start, pre_end)]
        post = group[group["game_date"].between(post_start, post_end)]
        if pre.empty or post.empty:
            continue
        pre_w = pre["pitch_count"].to_numpy(dtype=float)
        post_w = post["pitch_count"].to_numpy(dtype=float)
        pre_value = float(np.average(pre["value_per_100"], weights=pre_w))
        post_value = float(np.average(post["value_per_100"], weights=post_w))
        # Pre-trend: first half of pre window vs second half.
        midpoint = pre_start + (pre_end - pre_start) / 2
        early = pre[pre["game_date"] <= midpoint]
        late = pre[pre["game_date"] > midpoint]
        if early.empty or late.empty:
            pretrend = 0.0
        else:
            early_v = float(np.average(early["value_per_100"], weights=early["pitch_count"]))
            late_v = float(np.average(late["value_per_100"], weights=late["pitch_count"]))
            pretrend = late_v - early_v
        records.append(
            {
                **event.to_dict(),
                "player_name": group["player_name"].iloc[0],
                "p_throws": group["p_throws"].iloc[0],
                "pre_value_per_100": pre_value,
                "post_value_per_100": post_value,
                "delta_value_per_100": post_value - pre_value,
                "pretrend_delta": pretrend,
                "pre_csw": float(np.average(pre["csw_rate"], weights=pre_w)),
                "post_csw": float(np.average(post["csw_rate"], weights=post_w)),
                "pre_in_zone": float(np.average(pre["in_zone_rate"], weights=pre_w)),
                "post_in_zone": float(np.average(post["in_zone_rate"], weights=post_w)),
            }
        )
    return pd.DataFrame.from_records(records)


def _decision_for_case(delta: float, ci_low: float, durability: float) -> dict[str, str]:
    if delta >= 0.25 and ci_low > 0 and durability >= 0.55:
        return {
            "decision": "Reshape",
            "rejected": "Keep, De-emphasize",
            "confidence": "Moderate" if ci_low < 0.2 else "High",
        }
    if delta <= -0.15:
        return {
            "decision": "De-emphasize",
            "rejected": "Reshape, Keep",
            "confidence": "Low",
        }
    return {
        "decision": "Keep",
        "rejected": "Reshape, De-emphasize",
        "confidence": "Low" if abs(delta) < 0.15 else "Moderate",
    }


def run_locked_evaluation(settings: Settings) -> dict[str, Any]:
    """Execute the pre-committed locked evaluation and persist artifacts."""
    artifacts = settings.paths.artifacts
    artifacts.mkdir(parents=True, exist_ok=True)
    (artifacts / "models").mkdir(parents=True, exist_ok=True)
    (artifacts / "reports").mkdir(parents=True, exist_ok=True)

    frame = _load_pitch_frame(settings.paths.database)
    frame = frame.loc[frame["game_date"].dt.date >= settings.data.start_date].copy()
    boundaries = boundaries_from_settings(settings)
    frame["period"] = assign_period(frame["game_date"], boundaries)

    development = frame.loc[frame["period"].eq("development")]
    validation = frame.loc[frame["period"].eq("validation")]
    evaluation = frame.loc[frame["period"].eq("evaluation")]
    if development.empty or validation.empty or evaluation.empty:
        raise ValueError("Development, validation, and evaluation periods must be populated")

    # Train on a stratified sample if needed for runtime, but prefer large coverage.
    train_cap = 1_200_000
    if len(development) > train_cap:
        development_train = development.sample(train_cap, random_state=settings.project.random_seed)
    else:
        development_train = development

    model = fit_shape_value_model(development_train, random_seed=settings.project.random_seed)
    model_path = artifacts / "models" / "shape_value.joblib"
    joblib.dump(model, model_path)

    scored = _attach_predictions(pd.concat([development, validation, evaluation], ignore_index=True), model)
    game_shapes = aggregate_game_shapes(scored)
    game_values = _game_values(scored)
    candidates = thin_candidate_dates(game_shapes, stride_games=3)

    window = WindowSpec(
        pre_days=settings.interventions.pre_days,
        transition_days=settings.interventions.transition_days,
        post_days=settings.interventions.post_days,
        min_pitches=settings.interventions.min_pitches_each_side,
        min_games=settings.interventions.min_games_each_side,
    )
    comparisons = build_window_comparisons(
        game_shapes,
        spec=window,
        candidate_dates=candidates,
    )
    scored_changes = add_robust_change_scores(comparisons)
    scored_changes["period"] = assign_period(scored_changes["change_date"], boundaries)

    validation_changes = scored_changes.loc[scored_changes["period"].eq("validation")]
    threshold = freeze_threshold(validation_changes, quantile=0.90)

    validation_events = consolidate_episodes(validation_changes, z_threshold=threshold)
    evaluation_events = consolidate_episodes(
        scored_changes.loc[scored_changes["period"].eq("evaluation")],
        z_threshold=threshold,
    )

    # Natural controls: same window construction, but below the frozen threshold.
    control_windows = scored_changes.loc[scored_changes["max_abs_robust_z"] < threshold]
    control_sample_parts: list[pd.DataFrame] = []
    for _, group in control_windows.groupby("pitch_family", observed=True):
        control_sample_parts.append(
            group.sample(min(len(group), 250), random_state=settings.project.random_seed)
        )
    control_sample = (
        pd.concat(control_sample_parts, ignore_index=True)
        if control_sample_parts
        else control_windows.iloc[0:0].copy()
    )

    validation_outcomes = _window_outcome_deltas(
        game_values,
        validation_events,
        pre_days=window.pre_days,
        transition_days=window.transition_days,
        post_days=window.post_days,
    )
    evaluation_outcomes = _window_outcome_deltas(
        game_values,
        evaluation_events,
        pre_days=window.pre_days,
        transition_days=window.transition_days,
        post_days=window.post_days,
    )
    control_outcomes = _window_outcome_deltas(
        game_values,
        control_sample,
        pre_days=window.pre_days,
        transition_days=window.transition_days,
        post_days=window.post_days,
    )

    matches = match_controls(evaluation_outcomes, control_outcomes, caliper=1.35, n_matches=5)
    effect = estimate_effect(matches)

    # Pick a concrete case: largest positive matched effect among evaluation events.
    case: dict[str, Any]
    if not evaluation_outcomes.empty:
        case_row = evaluation_outcomes.sort_values("delta_value_per_100", ascending=False).iloc[0]
        case_matches = matches.loc[
            matches["treated_pitcher"].eq(case_row["pitcher"])
            & matches["treated_pitch_family"].eq(case_row["pitch_family"])
        ]
        case_delta = float(case_row["delta_value_per_100"])
        if not case_matches.empty:
            case_effect = float((case_matches["treated_delta"] - case_matches["control_delta"]).mean())
        else:
            case_effect = case_delta
        durability = float((evaluation_outcomes["delta_value_per_100"] > 0).mean())
        decision = _decision_for_case(case_effect, effect.ate_ci_low, durability)
        case = {
            "pitcher_id": int(case_row["pitcher"]),
            "player_name": str(case_row["player_name"]),
            "pitch_family": str(case_row["pitch_family"]),
            "p_throws": str(case_row["p_throws"]),
            "change_date": str(pd.Timestamp(case_row["change_date"]).date()),
            "primary_change_feature": str(case_row["primary_change_feature"]),
            "max_abs_robust_z": float(case_row["max_abs_robust_z"]),
            "pre_value_per_100": float(case_row["pre_value_per_100"]),
            "post_value_per_100": float(case_row["post_value_per_100"]),
            "delta_value_per_100": case_delta,
            "matched_delta_value_per_100": case_effect,
            "delta_release_speed": float(case_row.get("delta_release_speed", 0.0)),
            "delta_arm_side_break": float(case_row.get("delta_arm_side_break", 0.0)),
            "delta_induced_vertical_break": float(case_row.get("delta_induced_vertical_break", 0.0)),
            "pre_csw": float(case_row["pre_csw"]),
            "post_csw": float(case_row["post_csw"]),
            "pre_in_zone": float(case_row["pre_in_zone"]),
            "post_in_zone": float(case_row["post_in_zone"]),
            **decision,
        }
    else:
        case = {
            "decision": "Keep",
            "rejected": "Reshape, De-emphasize",
            "confidence": "Low",
            "player_name": "No eligible 2025 intervention",
            "pitch_family": "n/a",
            "matched_delta_value_per_100": 0.0,
            "delta_value_per_100": 0.0,
        }

    report = {
        "created_at_utc": datetime.now(UTC).isoformat(),
        "status": "locked_evaluation",
        "data": {
            "development_rows": int(len(development)),
            "validation_rows": int(len(validation)),
            "evaluation_rows": int(len(evaluation)),
            "training_rows_used": int(len(development_train)),
        },
        "threshold": {
            "metric": "max_abs_robust_z",
            "frozen_on": "validation_2024",
            "quantile": 0.90,
            "value": threshold,
        },
        "detection": {
            "validation_events": int(len(validation_events)),
            "evaluation_events": int(len(evaluation_events)),
            "candidate_windows": int(len(scored_changes)),
        },
        "effect": effect.to_dict(),
        "diagnostics": {
            "pretrend_gap": effect.pretrend_gap,
            "positive_share": effect.positive_share,
            "overlap_note": "Matched within pitch family using standardized pre-period shape and value.",
        },
        "case": case,
        "model_path": str(model_path),
    }

    report_path = artifacts / "reports" / "locked_evaluation.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    evaluation_outcomes.to_parquet(artifacts / "reports" / "evaluation_interventions.parquet", index=False)
    matches.to_parquet(artifacts / "reports" / "evaluation_matches.parquet", index=False)
    return report


def main() -> None:
    settings = load_settings()
    report = run_locked_evaluation(settings)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
