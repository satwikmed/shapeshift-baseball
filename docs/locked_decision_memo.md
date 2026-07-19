# ShapeShift locked decision memo

**Status:** Locked 2025 evaluation complete  
**To:** Baseball Operations leadership and Player Development  
**From:** Satwik Medipalli — independent public-data research  
**Subject:** Pitch-shape interventions — Keep by default; de-emphasize harmful patterns  
**Decision date:** 2026-07-19  
**Recommendation:** **KEEP** as organizational default; **DE-EMPHASIZE** specific harmful shape patterns  

## Decision in 30 seconds

Across 225 detected 2025 pitch-shape interventions, the matched average effect is
**+0.02 runs / 100 pitches** (80% CI: **-0.00 to +0.04**). That is operationally a
near-null. Public Statcast evidence does **not** support blanket pitch-redesign
programs. Development bandwidth should default to **Keep**, with Reshape reserved for
high-overlap exceptions and explicit rejection of shape patterns that underperform
matched controls.

| Item | Locked value |
|---|---:|
| Decision | Keep (default) / De-emphasize (harmful patterns) |
| Aggregate ATE | +0.02 RV / 100 |
| 80% interval | -0.00 to +0.04 |
| Treated events (2025) | 225 detected / 69 matched |
| Positive pair share | 57% |
| Pre-trend gap | +0.01 RV / 100 |
| Public-data confidence | Moderate for the null; case-level Moderate |

## Why this matters

Pitch grades answer “what shapes tend to work.” They do not answer whether asking a
pitcher to change is valuable on average. ShapeShift tests the intervention itself.

The locked result is uncomfortable and useful: **most detected shape changes are not
associated with meaningful matched gains.**

## Featured case — Andrés Muñoz, slider (2025-08-09)

| Attribute | Value |
|---|---:|
| Detected change | Arm-side break −2.3 in; velocity −1.7 mph |
| Robust change score | 2.9+ (above frozen 2024 threshold 2.95) |
| Matched delta | **−0.29 RV / 100** |
| Matches | 10 within pitch family |
| Pre → post CSW | 0.33 → 0.29 (approx. from event file) |
| Recommendation for analogs | **De-emphasize** this pattern |

Rejected alternatives for this pattern:

- **Reshape toward the same change:** rejected — matched value falls
- **Keep exploring similar sweep/arm-side shifts without tighter constraints:** rejected

## Evidence summary

1. **Outcome-blind detection** identified persistent physical changes without using results.
2. **Threshold frozen on 2024** validation robust-z (90th percentile = 2.95).
3. **2025 evaluation** applied that frozen rule — no re-tuning after peeking.
4. **Matched controls** were sub-threshold windows with similar pre-period shape/value.
5. **Aggregate effect fails to clear a meaningful development hurdle.**

## Implementation guidance

### Keep (default)
- Do not open an offseason pitch-design project from Stuff+/shape grades alone.
- Require a feasible analog, overlap check, and stop rules before Reshape.

### De-emphasize
- Kill candidates that resemble the Muñoz slider pattern: large arm-side break shifts
  with velocity loss and negative matched value.
- Reallocate bullpen time to command, usage, or pitches with stable support.

### Reshape (exception only)
- Allowed only when a candidate sits inside common support of historically helpful
  movement changes and passes command-stress and durability screens.

## What would change this decision

1. Internal TrackMan/Hawkeye confirming intent and measurement quality of the change
2. Medical/workload context explaining velocity loss
3. Stronger positive matched effects in a larger same-family cluster
4. Evidence that public pitch tags misclassified the intervention

## Methods note

Data: Baseball Savant Statcast, Hawkeye-era regular season focus, 5.6M+ pitches in
warehouse. Model trained on 2021–23 (1.2M-row working sample), threshold frozen on 2024,
effects estimated on 2025 only. Language remains associational. Full machine-readable
artifact: `artifacts/reports/locked_evaluation.json`.
