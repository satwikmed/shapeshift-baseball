"""DuckDB materialization and audit summaries."""

from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd

from shapeshift.data.features import add_canonical_pitch_features, flag_quality_issues
from shapeshift.data.outcomes import add_outcome_labels


def discover_partitions(raw_root: Path) -> list[Path]:
    """Return stable, sorted raw Statcast partitions."""
    return sorted(raw_root.glob("year=*/statcast_*.parquet"))


def build_pitch_table(raw_root: Path, database: Path) -> int:
    """Validate, transform, and upsert raw partitions into a canonical pitch table."""
    partitions = discover_partitions(raw_root)
    if not partitions:
        raise FileNotFoundError(f"No Statcast Parquet partitions found under {raw_root}")

    frames = [pd.read_parquet(path) for path in partitions]
    frames = [frame for frame in frames if not frame.empty]
    if not frames:
        raise FileNotFoundError(f"No non-empty Statcast partitions found under {raw_root}")
    pitches = add_outcome_labels(
        flag_quality_issues(add_canonical_pitch_features(pd.concat(frames, ignore_index=True)))
    )
    pitches = pitches.drop_duplicates(subset=["pitch_uid"], keep="last")

    database.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(database)) as connection:
        connection.register("pitch_frame", pitches)
        connection.execute("CREATE OR REPLACE TABLE pitches AS SELECT * FROM pitch_frame")
        connection.execute("CREATE UNIQUE INDEX IF NOT EXISTS pitch_uid_idx ON pitches (pitch_uid)")
        connection.execute(
            "CREATE INDEX IF NOT EXISTS pitcher_pitch_date_idx "
            "ON pitches (pitcher, pitch_family, game_date)"
        )
        row_count = connection.execute("SELECT count(*) FROM pitches").fetchone()
    return int(row_count[0]) if row_count else 0


def quality_summary(database: Path) -> pd.DataFrame:
    """Summarize exclusions and missingness for review."""
    with duckdb.connect(str(database), read_only=True) as connection:
        return connection.execute(
            """
            SELECT
                count(*) AS pitches,
                sum(qa_exclude_primary::INTEGER) AS excluded_primary,
                sum(qa_missing_identity::INTEGER) AS missing_identity,
                sum(qa_missing_shape::INTEGER) AS missing_shape,
                sum(qa_implausible_velocity::INTEGER) AS implausible_velocity,
                sum(qa_implausible_movement::INTEGER) AS implausible_movement,
                count(DISTINCT pitcher) AS pitchers,
                min(game_date) AS first_date,
                max(game_date) AS last_date
            FROM pitches
            """
        ).fetchdf()
