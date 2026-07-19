"""ShapeShift command-line interface."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from shapeshift.config import load_settings
from shapeshift.data.ingest import fetch_range
from shapeshift.data.store import build_pitch_table, quality_summary
from shapeshift.models.train import train_and_validate

app = typer.Typer(
    name="shapeshift",
    help="Analyze durable MLB pitch-shape interventions.",
    no_args_is_help=True,
)
console = Console()

ConfigOption = Annotated[
    Path,
    typer.Option("--config", "-c", help="Validated YAML configuration file."),
]


@app.command()
def fetch(
    start: Annotated[str, typer.Option(help="Inclusive start date (YYYY-MM-DD).")],
    end: Annotated[str, typer.Option(help="Inclusive end date (YYYY-MM-DD).")],
    config: ConfigOption = Path("config/default.yaml"),
    force: Annotated[bool, typer.Option(help="Replace existing partitions.")] = False,
) -> None:
    """Download resumable Statcast partitions."""
    settings = load_settings(config)
    try:
        start_date = date.fromisoformat(start)
        end_date = date.fromisoformat(end)
    except ValueError as error:
        raise typer.BadParameter("Dates must use YYYY-MM-DD format.") from error
    paths = fetch_range(
        start_date,
        end_date,
        settings.paths.raw,
        chunk_days=settings.data.chunk_days,
        force=force,
    )
    console.print(f"[green]Ready:[/green] {len(paths)} partition(s) in {settings.paths.raw}")


@app.command("build-store")
def build_store(config: ConfigOption = Path("config/default.yaml")) -> None:
    """Build the validated DuckDB pitch table."""
    settings = load_settings(config)
    rows = build_pitch_table(settings.paths.raw, settings.paths.database)
    console.print(f"[green]Ready:[/green] {rows:,} unique pitches in {settings.paths.database}")


@app.command()
def audit(config: ConfigOption = Path("config/default.yaml")) -> None:
    """Print the current data-quality scorecard."""
    settings = load_settings(config)
    summary = quality_summary(settings.paths.database)
    table = Table(title="ShapeShift data-quality scorecard")
    for column in summary.columns:
        table.add_column(column)
    table.add_row(*(str(value) for value in summary.iloc[0]))
    console.print(table)


@app.command("train-shape-model")
def train_shape_model(config: ConfigOption = Path("config/default.yaml")) -> None:
    """Train on development data and score the frozen validation period."""
    settings = load_settings(config)
    metadata = train_and_validate(settings)
    scorecard = metadata["scorecard"]
    console.print_json(data=scorecard)


@app.command("locked-eval")
def locked_eval(config: ConfigOption = Path("config/default.yaml")) -> None:
    """Run the frozen 2025 locked evaluation and write research artifacts."""
    from shapeshift.evaluation.locked import run_locked_evaluation

    settings = load_settings(config)
    report = run_locked_evaluation(settings)
    console.print_json(data={
        "evaluation_events": report["detection"]["evaluation_events"],
        "ate_per_100": report["effect"]["ate_per_100"],
        "ate_ci": [report["effect"]["ate_ci_low"], report["effect"]["ate_ci_high"]],
        "case": report["case"],
        "threshold": report["threshold"]["value"],
    })


if __name__ == "__main__":
    app()
