"""Resumable, date-partitioned Statcast ingestion."""

from __future__ import annotations

import hashlib
import json
import time
from collections.abc import Iterator
from dataclasses import asdict, dataclass
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

from shapeshift.data.schema import validate_columns


@dataclass(frozen=True)
class ExtractManifest:
    source: str
    start_date: str
    end_date: str
    rows: int
    columns: int
    sha256: str
    retrieved_at_utc: str


def date_chunks(start: date, end: date, chunk_days: int) -> Iterator[tuple[date, date]]:
    """Yield inclusive date chunks without crossing the requested end date."""
    if end < start:
        raise ValueError("end date must be on or after start date")
    if chunk_days < 1:
        raise ValueError("chunk_days must be positive")

    cursor = start
    while cursor <= end:
        chunk_end = min(cursor + timedelta(days=chunk_days - 1), end)
        yield cursor, chunk_end
        cursor = chunk_end + timedelta(days=1)


def partition_path(root: Path, start: date, end: date) -> Path:
    return root / f"year={start.year}" / f"statcast_{start.isoformat()}_{end.isoformat()}.parquet"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def fetch_chunk(
    start: date,
    end: date,
    output_root: Path,
    *,
    force: bool = False,
    max_attempts: int = 3,
) -> Path:
    """Fetch one chunk, validate it, and atomically persist Parquet plus provenance."""
    from pybaseball import statcast

    output = partition_path(output_root, start, end)
    manifest_path = output.with_suffix(".manifest.json")
    if output.exists() and manifest_path.exists() and not force:
        return output

    output.parent.mkdir(parents=True, exist_ok=True)
    last_error: Exception | None = None
    frame: pd.DataFrame | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            frame = statcast(
                start_dt=start.isoformat(),
                end_dt=end.isoformat(),
                verbose=False,
                parallel=True,
            )
            validate_columns(frame)
            break
        except Exception as error:
            last_error = error
            if attempt < max_attempts:
                time.sleep(2**attempt)
    if frame is None:
        raise RuntimeError(f"Statcast fetch failed after {max_attempts} attempts") from last_error

    temp_output = output.with_suffix(".parquet.tmp")
    if frame.empty:
        # Offseason windows can return zero rows; keep an empty, schema-free marker.
        pd.DataFrame().to_parquet(temp_output, index=False)
    else:
        frame.to_parquet(temp_output, index=False)
    temp_output.replace(output)

    manifest = ExtractManifest(
        source="MLB Baseball Savant via pybaseball",
        start_date=start.isoformat(),
        end_date=end.isoformat(),
        rows=len(frame),
        columns=0 if frame.empty else len(frame.columns),
        sha256=_sha256(output),
        retrieved_at_utc=pd.Timestamp.now(tz="UTC").isoformat(),
    )
    manifest_path.write_text(json.dumps(asdict(manifest), indent=2) + "\n", encoding="utf-8")
    return output


def fetch_range(
    start: date,
    end: date,
    output_root: Path,
    *,
    chunk_days: int = 7,
    force: bool = False,
) -> list[Path]:
    """Fetch a date range as independently resumable partitions."""
    from pybaseball import cache

    cache.enable()
    return [
        fetch_chunk(chunk_start, chunk_end, output_root, force=force)
        for chunk_start, chunk_end in date_chunks(start, end, chunk_days)
    ]
