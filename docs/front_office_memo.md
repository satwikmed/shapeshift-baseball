# ShapeShift decision memo

**Status:** Template — no player recommendation is valid until locked evaluation completes.

**To:** Baseball Operations leadership and Player Development  
**From:** Baseball Analytics  
**Subject:** [Pitcher] — [pitch] keep / reshape / abandon decision  
**Decision date:** [date]  
**Recommendation:** [KEEP / RESHAPE / ABANDON]  
**Rejected alternatives:** [list]

## Decision in 30 seconds

[One paragraph: exact proposed action, expected value range, confidence, and why the
rejected alternatives lose under uncertainty and feasibility.]

| Item | Decision value |
|---|---:|
| Decision | [Keep / Reshape / Abandon] |
| Proposed intervention | [e.g., +1.2 inches arm-side movement] or N/A |
| Expected run-value change / 100 pitches | [estimate and interval] |
| Zone-strike / CSW change | [estimate and interval] |
| Platoon-split change | [estimate and interval] |
| Arsenal cannibalization risk | [low / medium / high + estimate] |
| Usage-weighted seasonal value | [estimate and interval] |
| Durability probability | [calibrated probability] |
| Public-data confidence | [high / medium / low] |
| Recommended next checkpoint | [bullpen / live AB / monitor only] |

## Why this player

- **Role constraint:** [SP depth / swingman / leverage RP]
- **Current constraint:** [specific arsenal or shape issue]
- **Historical analogs:** [closest observed interventions, not merely player comps]
- **Arsenal fit:** [how the change interacts with primary fastball and other pitches]
- **Opportunity:** [usage, platoon, role, and acquisition/development relevance]

## Evidence

[Show the pre/post event-study estimate, uncertainty, pre-trend, and persistence. State
whether the result survives alternate windows, treatment thresholds, classification
checks, and command-stress tests.]

## Implementation card

| Attribute | Current | Target range | Guardrail |
|---|---:|---:|---:|
| Velocity | [ ] | [ ] | [ ] |
| Arm-side break | [ ] | [ ] | [ ] |
| Induced vertical break | [ ] | [ ] | [ ] |
| Release height | [ ] | [ ] | [ ] |
| Release side | [ ] | [ ] | [ ] |
| Extension | [ ] | [ ] | [ ] |

The target range must stay within changes observed among comparable pitchers. ShapeShift
does not infer a grip or mechanical cue from public data.

## Downside and stop conditions

- [Command or tunneling tradeoff]
- [Velocity/movement tradeoff]
- [Arsenal cannibalization]
- [Poor overlap or wide uncertainty]
- [Workload, health, or role consideration unavailable publicly]
- Stop if [measurable bullpen/live-AB criterion].

## What internal information would change the decision

1. Hawkeye ball-flight and release measurements: [specific check]
2. Grip, intent, and biomechanics: [specific check]
3. Player and coach feasibility assessment: [specific check]
4. Medical/workload context: [specific check]
5. Internal scouting or pitch-classification evidence: [specific check]

## Methods note

The estimate is observational and uses public Statcast tracking data. Interventions are
detected from physical changes without inspecting outcomes, then evaluated against matched
not-yet-treated controls. The memo will use causal language only if overlap, balance,
pre-trend, placebo, and sensitivity diagnostics support it. Shape grades are covariates,
not the recommendation itself.
