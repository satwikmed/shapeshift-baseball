# ShapeShift

**Which pitch-shape changes create durable value, and who should try them next?**

ShapeShift is a decision-support research project for MLB player development and
acquisition. It detects material changes in a pitcher's pitch shape, estimates the
out-of-sample value associated with those interventions, and recommends a constrained
**Keep / Reshape / Abandon** decision for comparable pitchers.

This is deliberately not another public Stuff+ leaderboard. Shape grades are covariates.
The unit of analysis is an **intervention**: a pitcher changes the velocity, movement,
release, or usage of one offering while preserving enough pre- and post-change
observations to evaluate it.

## Decision outputs

ShapeShift will ship three views of the same analysis:

1. **Front-office memo** — Keep / Reshape / Abandon, rejected alternatives, expected
   value, confidence, and what proprietary evidence would change the decision.
2. **Coach card** — a one-page plan with cues, checkpoints, and stop rules.
3. **Analyst workbench** — reproducible data lineage, model validation, sensitivity
   analysis, intervention explorer, and candidate ranking.

## Research question

> Among MLB pitchers who materially changed a pitch's shape or velocity, which changes
> improved context-neutral expected run value in future periods, and which current
> pitchers are credible candidates for analogous changes?

### Primary estimand

The primary quantity is the change in expected runs allowed per 100 pitches attributable
to a detected intervention over the following 60 days, relative to a matched
not-yet-treated comparison set. Results are reported with uncertainty and as
decision-support evidence—not as proof that public tracking data establishes causality.

### Pre-committed evaluation rules

- Detect interventions using only physical pitch characteristics, never outcomes.
- Require minimum pre/post pitch counts and persistence across multiple appearances.
- Train outcome models with forward-chaining season or date splits—never random pitch
  splits for headline results.
- Keep pitcher identity out of the shape-quality model.
- Compare against simple baselines and report calibration, discrimination, and
  year-ahead reliability.
- Estimate heterogeneous effects only after the aggregate design passes placebo and
  pre-trend checks.
- Report null and negative findings; no cherry-picked success-only leaderboard.

The full protocol is in [`docs/research_protocol.md`](docs/research_protocol.md).

## Planned pipeline

```text
Baseball Savant
  -> date-partitioned raw Parquet + provenance
  -> validated DuckDB pitch table
  -> pitcher/pitch rolling shape states
  -> intervention candidates
  -> context-neutral pitch-value model
  -> matched event study + uncertainty
  -> feasible candidate recommendations
```

## Local setup

Requires Python 3.11–3.13 and [`uv`](https://docs.astral.sh/uv/).

```bash
uv sync
uv run shapeshift --help
uv run pytest
```

Run the decision website:

```bash
cd web
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). Until locked evaluation finishes,
the website uses an anonymized, clearly labeled illustrative case rather than presenting
fabricated player findings.

Public Statcast data is large. Development commands default to narrow date windows and
cache every raw response. Full-history runs are explicitly requested and resumable.

Modeling uses the Hawkeye-era regular season (2021–2025). Location fields are excluded
from the shape model, especially important under 2026 ABS plate/zone definition changes.

## Status

The project is under active development. Model rankings are not yet research findings.

## Data and attribution

Data is sourced from MLB Baseball Savant via `pybaseball`. ShapeShift is an independent
research project and is not affiliated with Major League Baseball or the Boston Red Sox.
Raw Statcast data is not committed to this repository.
