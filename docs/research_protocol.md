# ShapeShift research protocol

Version: 0.2 (pre-analysis draft)

Influences incorporated from public research and application-review standards:
intervention identification over Stuff+ cloning; keep / reshape / abandon decisions;
zone-strike and platoon-neutrality secondary outcomes; explicit coach stop rules.

## 1. Baseball decision

A player-development group has limited offseason and in-season training bandwidth. The
decision is not merely whether a pitch grades well. It is whether to ask a specific
pitcher to keep, reshape, or de-emphasize a specific pitch under role and feasibility
constraints.

For each pitcher–pitch case, ShapeShift must choose exactly one of:

1. **Keep** the current pitch as-is.
2. **Reshape** it toward a defined, physically supported target.
3. **De-emphasize / abandon** it in favor of an existing secondary.

Acquisition relevance is secondary: a reshape recommendation can also flag a player as a
tractable development target. "Do nothing" is expressed as Keep when expected benefit does
not clear uncertainty, feasibility, or arsenal risk.

## 2. Confirmatory question

Among pitcher–pitch-type pairs with a persistent, material physical change, what is the
average change in context-neutral expected runs allowed per 100 pitches during the next
60 days, compared with observationally similar pitcher–pitch-type pairs that have not yet
changed?

### 2.1 Unit of analysis

An intervention is indexed by pitcher, canonical pitch family, and detected change date.
The pre-period is days -60 through -8. The transition buffer is days -7 through +7. The
post-period is days +8 through +67. Alternate 30- and 90-day windows are sensitivity
analyses.

### 2.2 Treatment definition

Treatment is detected without outcome information. A candidate must:

- have at least 100 pitches in both pre- and post-periods;
- appear in at least three games on each side;
- exceed a robust, pitch-family-specific threshold in at least one physical dimension;
- retain the new state in at least 70% of post-period rolling windows; and
- not be explained solely by a tracking-system discontinuity or pitch relabeling.

Physical dimensions include velocity, arm-side horizontal movement, induced vertical
movement, release height/side, extension, spin rate, and arsenal-relative differentials.
Horizontal quantities are mirrored so positive values always represent arm-side movement.

Thresholds are learned from robust within-pitcher variability in the training era and
frozen before evaluation.

### 2.3 Primary outcome

The primary outcome is the mean predicted run value per 100 pitches from a cross-fitted,
context-neutral shape model. The model uses physical flight and release characteristics,
pitch family, batter handedness, and fastball-relative differentials. It excludes plate
location, count, score, observed pitch result, pitcher identity, and post-pitch variables.

Observed `delta_run_exp` is retained for model training and secondary descriptive checks,
with sign standardized so larger values are better for the pitcher.

### 2.4 Secondary outcomes

- called-strike-plus-whiff (CSW) probability;
- in-zone rate and in-zone miss rate for the treated pitch;
- platoon split change (same-side vs opposite-side expected run value);
- hard-contact probability conditional on contact;
- usage change and cannibalization of other pitches' expected run value;
- same-pitch physical persistence at 30, 60, and 90 days;
- subsequent-period strikeout-minus-walk rate at pitcher level.

Secondary outcomes do not replace a null primary result.
Zone-strike and platoon metrics are reported because optimizing whiff alone can conflict
with strike-throwing and platoon-neutrality goals.

## 3. Identification strategy

This is an observational study. The headline estimate uses a staggered matched event study
with not-yet-treated controls.

### 3.1 Matching variables

Controls are matched on pre-period:

- pitch family and pitcher handedness;
- age band and role (starter/reliever);
- velocity, movement, release, extension, and usage;
- baseline shape-model value and trend;
- opponent-handedness mix;
- calendar month and season.

Matching and weighting choices are fit in the training era. Covariate balance is reported
before and after weighting.

### 3.2 Required diagnostics

- event-time pre-trends;
- placebo intervention dates;
- negative-control outcomes;
- overlap and effective sample size;
- leave-one-season-out estimates;
- sensitivity to treatment thresholds and windows;
- estimates with and without players returning from long absences;
- classification sensitivity (official tags vs continuous shape neighborhoods);
- survivorship check for abandoned experiments;
- command-stress tests (location consistency deterioration);
- arsenal cannibalization under usage shifts.

The write-up will use "associated with" unless diagnostics and design justify stronger
language. No public-data design can isolate coaching, injury, intent, grip, or mechanical
changes that are unobserved.

## 4. Prediction and recommendation

Candidate recommendations are distinct from intervention effect estimation.

For each current pitcher–pitch pair, the system searches only within changes previously
observed among biomechanically comparable public-data profiles. Proposed changes must:

- remain inside the empirical support of release and movement combinations;
- respect pitch-family and handedness constraints;
- avoid recommending multiple simultaneous dimensions unless observed together;
- include prediction intervals and nearest historical analogs; and
- be withheld when support or model agreement is insufficient.

The candidate score combines expected run-value lift, probability of a durable change,
usage-weighted opportunity, uncertainty, and an explicit implementation-risk penalty.
The exact weighting will be displayed and sensitivity-tested.

Every recommendation must name the rejected alternatives. A Keep decision is preferred
whenever reshape or abandon depends on extrapolation, weak overlap, or command collapse.

## 5. Data splits

- **Modeling core:** Hawkeye-era regular season, 2021–2025.
- **Model development:** 2021–2023.
- **Validation and threshold freezing:** 2024.
- **Locked evaluation:** 2025.
- **Prospective candidate board:** 2026 season-to-date, never used for performance claims.
- **Pre-2021 archive:** optional sensitivity only; not used for headline estimates.

The 2020 season is excluded from the core because of schedule/environment and incomplete
arm-angle coverage relative to the Hawkeye design era. Automated tests enforce temporal
boundaries.

**2026 ABS caution:** Savant plate/zone definitions change under ABS. Location metrics are
never used in the Stuff / shape model and must not be pooled naively with 2021–2025 for
any Location companion analysis.

## 6. Model scorecard

The shape model must beat:

1. pitch-family mean;
2. regularized linear / logistic baseline; and
3. a compact generalized additive or tree baseline where practical.

Report:

- multiclass log loss or component Brier scores;
- expected calibration error and reliability plots;
- run-value RMSE/MAE at pitch and pitcher–pitch aggregate levels;
- year-to-year reliability after empirical-Bayes shrinkage;
- subgroup performance by pitch family, handedness, and role.

A complex model is rejected if gains are trivial or unstable.
Shape grades are covariates and diagnostics, not the product.

## 7. Failure criteria

The project will not publish a positive recommendation leaderboard if:

- treatment and control pre-trends materially diverge;
- overlap is poor for the majority of interventions;
- aggregate effects reverse under reasonable specifications;
- candidate counterfactuals rely on extrapolation; or
- tracking changes cannot be separated from player changes.

A well-supported null result is acceptable and will be reported as such.

## 8. Communication standard

Every player recommendation must answer:

1. Keep, reshape, or abandon — and what was rejected?
2. Why might it help this player specifically?
3. How large is the expected benefit and uncertainty?
4. What could go wrong?
5. What are the stop rules?
6. What internal data or coach observation would confirm or reject it?

The technical appendix must make every displayed number traceable to a data snapshot,
configuration, and model artifact.

Deliverables are three distinct artifacts:

1. leadership memo;
2. coach one-pager with drills and stop rules;
3. analyst appendix with identification diagnostics.
