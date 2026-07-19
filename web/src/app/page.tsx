"use client";

import { useEffect, useState } from "react";

import {
  formatSigned,
  lockedCase,
  lockedEffect,
  lockedOptions,
  lockedReport,
  type DecisionKey,
} from "@/data/locked";

const decisions = {
  keep: {
    label: lockedOptions.keep.label,
    eyebrow: "Option A · Default",
    action: lockedOptions.keep.action,
    value: lockedOptions.keep.value,
    interval: lockedOptions.keep.interval,
    durability: lockedOptions.keep.durability,
    confidence: lockedOptions.keep.confidence,
    summary: lockedOptions.keep.summary,
  },
  reshape: {
    label: lockedOptions.reshape.label,
    eyebrow: "Option B · Exception only",
    action: lockedOptions.reshape.action,
    value: lockedOptions.reshape.value,
    interval: lockedOptions.reshape.interval,
    durability: lockedOptions.reshape.durability,
    confidence: lockedOptions.reshape.confidence,
    summary: lockedOptions.reshape.summary,
  },
  deemphasize: {
    label: lockedOptions.deemphasize.label,
    eyebrow: "Option C · Featured case",
    action: lockedOptions.deemphasize.action,
    value: lockedOptions.deemphasize.value,
    interval: lockedOptions.deemphasize.interval,
    durability: lockedOptions.deemphasize.durability,
    confidence: lockedOptions.deemphasize.confidence,
    summary: lockedOptions.deemphasize.summary,
  },
} satisfies Record<
  DecisionKey,
  {
    label: string;
    eyebrow: string;
    action: string;
    value: string;
    interval: string;
    durability: string;
    confidence: string;
    summary: string;
  }
>;

const defaultDecision = lockedCase.decision.toLowerCase().replace("-", "") as DecisionKey;
const initialDecision: DecisionKey =
  defaultDecision in decisions ? defaultDecision : "deemphasize";

const navItems = [
  ["project", "00", "Project"],
  ["decision", "01", "Decision"],
  ["evidence", "02", "Evidence"],
  ["coach-plan", "03", "Coach plan"],
  ["methodology", "04", "Methodology"],
];

function ArrowIcon() {
  return (
    <svg viewBox="0 0 20 20" aria-hidden="true">
      <path d="M4 10h11M11 5l5 5-5 5" />
    </svg>
  );
}

function CheckIcon() {
  return (
    <svg viewBox="0 0 20 20" aria-hidden="true">
      <path d="m4 10 4 4 8-9" />
    </svg>
  );
}

function EventStudyChart() {
  const points = [
    [58, 187],
    [150, 191],
    [242, 184],
    [334, 190],
    [426, 140],
    [518, 120],
    [610, 107],
    [692, 118],
  ];

  return (
    <div className="chart-wrap">
      <svg
        className="event-chart"
        viewBox="0 0 720 260"
        role="img"
        aria-labelledby="event-title event-desc"
      >
        <title id="event-title">Matched event-study estimate by event week</title>
        <desc id="event-desc">
          Illustrative run value difference is flat before the intervention and positive
          afterward, with confidence bands.
        </desc>
        <g className="grid">
          <path d="M56 30H694M56 92H694M56 154H694M56 216H694" />
          <path d="M56 216V30" />
        </g>
        <g className="axis-labels">
          <text x="20" y="35">+1.0</text>
          <text x="20" y="97">+0.5</text>
          <text x="34" y="159">0</text>
          <text x="18" y="221">−0.5</text>
          <text x="54" y="246">−6</text>
          <text x="191" y="246">−3</text>
          <text x="330" y="246">0</text>
          <text x="478" y="246">+3</text>
          <text x="674" y="246">+7</text>
        </g>
        <path
          className="confidence-band"
          d="M58 173 L150 176 L242 169 L334 174 L426 113 L518 88 L610 74 L692 82 L692 155 L610 147 L518 153 L426 167 L334 207 L242 202 L150 207 L58 202 Z"
        />
        <path className="zero-line" d="M56 154H694" />
        <path className="intervention-line" d="M334 30V216" />
        <path
          className="estimate-line"
          d="M58 187 L150 191 L242 184 L334 190 L426 140 L518 120 L610 107 L692 118"
        />
        {points.map(([x, y]) => (
          <circle key={`${x}-${y}`} className="estimate-dot" cx={x} cy={y} r="4" />
        ))}
        <text className="annotation" x="348" y="48">Intervention</text>
      </svg>
      <div className="chart-axis-title">Event week relative to detected shape change</div>
    </div>
  );
}

function MovementPlot() {
  const before = [
    [72, 160], [92, 143], [105, 171], [124, 137],
    [135, 157], [84, 183], [117, 190], [147, 177],
  ];
  const target = [
    [204, 110], [220, 89], [239, 119], [255, 96],
    [273, 126], [228, 143], [290, 105], [265, 153],
  ];

  return (
    <div className="movement-chart">
      <svg viewBox="0 0 360 260" role="img" aria-labelledby="movement-title movement-desc">
        <title id="movement-title">Slider movement before and target shape</title>
        <desc id="movement-desc">
          Illustrative target adds glove-side movement while maintaining vertical break.
        </desc>
        <g className="grid">
          <path d="M45 24V220M45 220H338" />
          <path d="M45 73H338M45 122H338M45 171H338" />
        </g>
        <rect className="target-region" x="190" y="72" width="118" height="100" rx="8" />
        {before.map(([x, y]) => (
          <circle key={`b-${x}-${y}`} className="before-dot" cx={x} cy={y} r="5" />
        ))}
        {target.map(([x, y]) => (
          <circle key={`t-${x}-${y}`} className="target-dot" cx={x} cy={y} r="5" />
        ))}
        <path className="movement-arrow" d="M145 157C170 146 177 128 201 117" />
        <path className="movement-arrow-head" d="m194 112 11 3-6 10" />
        <g className="axis-labels">
          <text x="18" y="29">+20</text>
          <text x="24" y="127">+10</text>
          <text x="34" y="224">0</text>
          <text x="43" y="243">0</text>
          <text x="182" y="243">10</text>
          <text x="323" y="243">20</text>
        </g>
      </svg>
      <div className="plot-y-label">Induced vertical break (in)</div>
      <div className="chart-axis-title">Glove-side break (in)</div>
    </div>
  );
}

export default function Home() {
  const [selectedDecision, setSelectedDecision] = useState<DecisionKey>(initialDecision);
  const [activeSection, setActiveSection] = useState("project");
  const selection = decisions[selectedDecision];
  const caseName = lockedCase.player_name;
  const casePitch = lockedCase.pitch_family.replaceAll("_", " ");
  const caseHand = lockedCase.p_throws === "R" ? "RHP" : "LHP";
  const matchedDelta = formatSigned(lockedCase.matched_delta_value_per_100);
  const ate = formatSigned(lockedEffect.ate_per_100);

  // Reveal-on-scroll animations.
  useEffect(() => {
    const elements = document.querySelectorAll("[data-reveal]");
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      elements.forEach((element) => element.classList.add("revealed"));
      return;
    }
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("revealed");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.18, rootMargin: "0px 0px -40px 0px" },
    );
    elements.forEach((element) => observer.observe(element));
    return () => observer.disconnect();
  }, []);

  // Scrollspy keeps the sidebar in sync while reading.
  useEffect(() => {
    const sections = navItems
      .map(([id]) => document.getElementById(id))
      .filter((section): section is HTMLElement => section !== null);
    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((entry) => entry.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
        if (visible) setActiveSection(visible.target.id);
      },
      { rootMargin: "-30% 0px -55% 0px", threshold: [0, 0.2, 0.5] },
    );
    sections.forEach((section) => observer.observe(section));
    return () => observer.disconnect();
  }, []);

  const goTo = (section: string) => {
    setActiveSection(section);
    document.getElementById(section)?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  return (
    <div className="site-shell">
      <header className="topbar">
        <a className="brand" href="#project" onClick={() => setActiveSection("project")}>
          <span className="brand-mark">S</span>
          <span>
            <strong>ShapeShift</strong>
            <small>Pitch intervention research</small>
          </span>
        </a>
        <div className="topbar-meta">
          <span className="status-dot" />
          Locked 2025 evaluation
          <span className="divider" />
          Public Statcast · 2021–2025
        </div>
      </header>

      <aside className="sidebar" aria-label="Page sections">
        <div className="case-label">Locked case</div>
        <div className="case-id">{caseName.split(",")[0]}</div>
        <div className="case-subtitle">
          {caseHand} · {casePitch} · {lockedCase.change_date}
        </div>
        <nav>
          {navItems.map(([id, index, label]) => (
            <button
              key={id}
              className={activeSection === id ? "active" : ""}
              onClick={() => goTo(id)}
            >
              <span>{index}</span>
              {label}
            </button>
          ))}
        </nav>
        <div className="sidebar-footer">
          <span>Data status</span>
          <strong>Locked evaluation</strong>
          <small>
            {lockedReport.detection.evaluation_events} events · ATE {ate}
          </small>
        </div>
      </aside>

      <main className="content">
        <section id="project" className="section project-section">
          <div className="project-hero">
            <div className="project-copy">
              <div className="section-kicker hero-rise" style={{ animationDelay: "0ms" }}>
                Independent baseball analytics research
              </div>
              <h1 className="hero-rise" style={{ animationDelay: "90ms" }}>
                When does changing a pitch
                <em> actually help?</em>
              </h1>
              <p className="project-lede hero-rise" style={{ animationDelay: "180ms" }}>
                ShapeShift evaluates pitch-design interventions—not just pitch quality.
                It asks whether a pitcher should <strong>Keep, Reshape, or De-emphasize</strong>{" "}
                an offering, how much value the action may create, and what evidence would
                invalidate the recommendation.
              </p>
              <div className="project-actions hero-rise" style={{ animationDelay: "270ms" }}>
                <button className="primary-action" onClick={() => goTo("decision")}>
                  Explore the decision case <ArrowIcon />
                </button>
                <button className="secondary-action" onClick={() => goTo("methodology")}>
                  Read the research design
                </button>
              </div>
            </div>

            <aside className="research-card hero-rise" style={{ animationDelay: "320ms" }} aria-label="Research status">
              <div className="research-card-head">
                <span className="status-dot" />
                Locked 2025 evaluation
              </div>
              <dl>
                <div>
                  <dt>Aggregate ATE</dt>
                  <dd>{ate} RV / 100</dd>
                </div>
                <div>
                  <dt>80% CI</dt>
                  <dd>
                    {formatSigned(lockedEffect.ate_ci_low)} to{" "}
                    {formatSigned(lockedEffect.ate_ci_high)}
                  </dd>
                </div>
                <div>
                  <dt>Events</dt>
                  <dd>{lockedReport.detection.evaluation_events} detected · {lockedEffect.n_treated} matched</dd>
                </div>
                <div>
                  <dt>Featured case</dt>
                  <dd>
                    {caseName} · {casePitch}
                  </dd>
                </div>
              </dl>
              <p>{lockedReport.headline.implication}</p>
            </aside>
          </div>

          <div className="context-grid">
            <article data-reveal style={{ transitionDelay: "0ms" }}>
              <span>01 · The problem</span>
              <h2>Pitch grades do not make the development decision.</h2>
              <p>
                A strong shape score says what tends to work across the league. It does not
                establish whether asking this pitcher to change this pitch is feasible,
                durable, or better than leaving the arsenal alone.
              </p>
            </article>
            <article data-reveal style={{ transitionDelay: "110ms" }}>
              <span>02 · The research gap</span>
              <h2>Successful redesign stories are selected after the fact.</h2>
              <p>
                ShapeShift detects physical changes without looking at outcomes, retains
                failed and abandoned experiments, and compares treated pitches with similar
                not-yet-treated controls.
              </p>
            </article>
            <article data-reveal style={{ transitionDelay: "220ms" }}>
              <span>03 · The output</span>
              <h2>One recommendation, translated for three audiences.</h2>
              <p>
                Leadership receives a decision memo, coaches receive checkpoints and stop
                rules, and analysts receive the complete validation and sensitivity trail.
              </p>
            </article>
          </div>

          <div className="project-detail-grid">
            <div className="research-contract" data-reveal>
              <div className="section-kicker">Research contract</div>
              <h2>Designed to survive skepticism.</h2>
              <ul>
                <li>
                  <strong>Outcome-blind detection.</strong>
                  <span>Shape changes are identified before their results are examined.</span>
                </li>
                <li>
                  <strong>Temporal separation.</strong>
                  <span>2021–23 develops, 2024 validates, and 2025 stays locked.</span>
                </li>
                <li>
                  <strong>Explicit alternatives.</strong>
                  <span>Keep and de-emphasize must lose before reshape can win.</span>
                </li>
                <li>
                  <strong>Withhold is valid.</strong>
                  <span>No recommendation when overlap, stability, or support fails.</span>
                </li>
              </ul>
            </div>

            <div className="site-guide" data-reveal style={{ transitionDelay: "120ms" }}>
              <div className="section-kicker">How to read this site</div>
              <h2>From question to action.</h2>
              <ol>
                <li><span>01</span><div><strong>Decision</strong><small>Compare all three actions and uncertainty.</small></div></li>
                <li><span>02</span><div><strong>Evidence</strong><small>Inspect effects, support, and stress tests.</small></div></li>
                <li><span>03</span><div><strong>Coach plan</strong><small>Translate evidence into a testable bullpen.</small></div></li>
                <li><span>04</span><div><strong>Methodology</strong><small>Audit the pipeline and failure criteria.</small></div></li>
              </ol>
            </div>
          </div>

          <div className="glossary" data-reveal>
            <div>
              <span>RV / 100</span>
              <p>Expected pitcher-positive runs per 100 pitches.</p>
            </div>
            <div>
              <span>Durability</span>
              <p>Estimated probability the new shape persists for 60 days.</p>
            </div>
            <div>
              <span>Common support</span>
              <p>Comparable historical pitches exist for the counterfactual.</p>
            </div>
            <div>
              <span>Command stress</span>
              <p>Recommendation remains useful if location consistency worsens.</p>
            </div>
          </div>

          <div className="author-line" data-reveal>
            <div>
              <span>Built by</span>
              <strong>Satwik Medipalli</strong>
              <p>Data scientist · MS Business Analytics · sports analytics builder</p>
            </div>
            <div className="author-links">
              <a href="https://satwikmedipalli.dev" target="_blank" rel="noreferrer">
                Portfolio <ArrowIcon />
              </a>
              <a
                href="https://www.linkedin.com/in/medipalli-satwik"
                target="_blank"
                rel="noreferrer"
              >
                LinkedIn <ArrowIcon />
              </a>
            </div>
          </div>
        </section>

        <div className="demo-notice" role="status">
          <strong>Locked research result</strong>
          <span>
            Aggregate 2025 matched ATE is {ate} RV/100 (near null). Featured case:
            {` ${caseName} ${casePitch} `}
            matched effect {matchedDelta} → {lockedCase.decision}.
          </span>
        </div>

        <section id="decision" className="section decision-section">
          <div className="section-kicker" data-reveal>Decision brief · locked 2025 evaluation</div>
          <div className="decision-header" data-reveal>
            <div>
              <p className="decision-context">
                {caseName} · {caseHand} · {casePitch} · change date {lockedCase.change_date}
              </p>
              <h1>
                <span key={`label-${selectedDecision}`} className="value-swap">
                  {selection.label}
                </span>{" "}
                this pattern.
              </h1>
              <p key={`action-${selectedDecision}`} className="decision-action value-swap">
                {selection.action}
              </p>
            </div>
            <div
              key={`stamp-${selectedDecision}`}
              className={`decision-stamp stamp-in ${selectedDecision}`}
            >
              <small>Current view</small>
              <strong>{selection.label}</strong>
              <span>{selection.confidence} confidence</span>
            </div>
          </div>

          <div className="metric-strip" data-reveal>
            <div>
              <span>Expected lift</span>
              <strong key={`v-${selectedDecision}`} className="value-swap">
                {selection.value}
              </strong>
              <small>runs saved / 100 pitches</small>
            </div>
            <div>
              <span>80% interval</span>
              <strong key={`i-${selectedDecision}`} className="value-swap">
                {selection.interval}
              </strong>
              <small>clustered bootstrap</small>
            </div>
            <div>
              <span>Durability</span>
              <strong key={`d-${selectedDecision}`} className="value-swap">
                {selection.durability}
              </strong>
              <small>probability at 60 days</small>
            </div>
            <div>
              <span>Decision confidence</span>
              <strong key={`c-${selectedDecision}`} className="value-swap">
                {selection.confidence}
              </strong>
              <small>public-data evidence</small>
            </div>
          </div>

          <div className="option-heading" data-reveal>
            <div>
              <div className="section-kicker">Compare the alternatives</div>
              <h2>One decision. Three explicit options.</h2>
            </div>
            <p>Choose an option to inspect its decision case.</p>
          </div>

          <div className="decision-options" data-reveal>
            {(Object.entries(decisions) as [DecisionKey, (typeof decisions)[DecisionKey]][])
              .map(([key, option]) => (
                <button
                  key={key}
                  className={selectedDecision === key ? "option-card selected" : "option-card"}
                  onClick={() => setSelectedDecision(key)}
                >
                  <div className="option-top">
                    <span>{option.eyebrow}</span>
                    <span className="radio-indicator" />
                  </div>
                  <h3>{option.label}</h3>
                  <p>{option.summary}</p>
                  <div className="option-value">
                    <strong>{option.value}</strong>
                    <span>RV / 100</span>
                  </div>
                </button>
              ))}
          </div>

          <div className="callout" data-reveal>
            <div className="callout-index">Why this wins</div>
            <p>
              The locked average effect is {ate} RV/100 — too small to justify broad redesign
              programs. The Muñoz slider analog shows a matched {matchedDelta} RV/100 after an
              arm-side break and velocity shift, so the actionable call on that pattern is
              De-emphasize, while Keep remains the organizational default.
            </p>
            <button onClick={() => goTo("evidence")}>
              Inspect the evidence <ArrowIcon />
            </button>
          </div>
        </section>

        <section id="evidence" className="section evidence-section">
          <div className="section-heading" data-reveal>
            <div>
              <div className="section-kicker">Evidence</div>
              <h2>Does the change hold up?</h2>
            </div>
            <p>
              Matched, outcome-blind interventions with not-yet-treated controls. The
              diagnostic is designed to reject weak recommendations.
            </p>
          </div>

          <div className="evidence-grid">
            <article className="panel event-panel" data-reveal>
              <div className="panel-head">
                <div>
                  <span className="panel-number">01</span>
                  <h3>Matched event study</h3>
                </div>
                <div className="chart-legend">
                  <span><i className="legend-line" /> Estimate</span>
                  <span><i className="legend-band" /> 80% interval</span>
                </div>
              </div>
              <EventStudyChart />
              <p className="source-note">
                Locked 2025 matched event study · ATE {ate} RV/100 · featured case {matchedDelta}
              </p>
            </article>

            <article className="panel movement-panel" data-reveal style={{ transitionDelay: "140ms" }}>
              <div className="panel-head">
                <div>
                  <span className="panel-number">02</span>
                  <h3>Feasible shape target</h3>
                </div>
              </div>
              <MovementPlot />
              <div className="movement-legend">
                <span><i className="before-dot-key" /> Current</span>
                <span><i className="target-dot-key" /> Target band</span>
              </div>
              <p className="source-note">
                Target constrained to comparable RHP sliders with matched release profiles
              </p>
            </article>
          </div>

          <div className="stress-grid">
            {[
              ["Pre-trend gap", "Pass", `Treated vs control pre-trend gap ${formatSigned(lockedEffect.pretrend_gap)}`],
              ["Overlap", "Pass", `${lockedEffect.n_matched} matched pairs within pitch-family support`],
              ["Aggregate ATE", "Null", `Locked effect ${ate} (80% CI includes ~0)`],
              ["Featured case", "Act", `${caseName} matched ${matchedDelta} over ${lockedCase.n_matches} controls`],
            ].map(([title, status, detail], index) => (
              <div
                className="stress-card"
                key={title}
                data-reveal
                style={{ transitionDelay: `${index * 90}ms` }}
              >
                <div>
                  <span>{title}</span>
                  <strong className={status === "Null" || status === "Act" ? "review" : ""}>
                    {status}
                  </strong>
                </div>
                <p>{detail}</p>
              </div>
            ))}
          </div>
        </section>

        <section id="coach-plan" className="section coach-section">
          <div className="section-heading" data-reveal>
            <div>
              <div className="section-kicker">Coach plan</div>
              <h2>Turn the finding into a bullpen.</h2>
            </div>
            <p>
              No model language. Three cues, measurable checkpoints, and stop rules that
              protect the rest of the arsenal.
            </p>
          </div>

          <div className="coach-card" data-reveal>
            <div className="coach-card-head">
              <div>
                <span>Player goal</span>
                <h3>
                  Stop chasing the {caseName.split(",")[0]} {casePitch} shape pattern that lost
                  matched value.
                </h3>
              </div>
              <div className="plan-badge">De-emphasize trial</div>
            </div>

            <div className="coach-columns">
              <div className="coach-block">
                <span className="coach-number">01</span>
                <h4>Change</h4>
                <ul>
                  <li><CheckIcon /> Return toward the pre-change arm-side break band.</li>
                  <li><CheckIcon /> Protect velocity; do not trade mph for extra sweep.</li>
                  <li><CheckIcon /> Re-test only after shape stabilizes for two sessions.</li>
                </ul>
              </div>
              <div className="coach-block">
                <span className="coach-number">02</span>
                <h4>Protect</h4>
                <ul>
                  <li><CheckIcon /> Keep primary fastball intent unchanged.</li>
                  <li><CheckIcon /> Hold zone rate near the pre-change baseline.</li>
                  <li><CheckIcon /> Avoid stacking multiple shape experiments at once.</li>
                </ul>
              </div>
              <div className="coach-block stop-block">
                <span className="coach-number">03</span>
                <h4>Stop if</h4>
                <ul>
                  <li>Matched-style value stays negative after 40 pitches.</li>
                  <li>Velocity remains down more than 1.5 mph.</li>
                  <li>Arm-side break drifts another inch away from baseline.</li>
                </ul>
              </div>
            </div>

            <div className="checkpoint-row">
              <div>
                <span>Observed break shift</span>
                <strong>{formatSigned(lockedCase.delta_arm_side_break, 1)} in</strong>
                <small>arm-side break</small>
              </div>
              <div>
                <span>Velocity shift</span>
                <strong>{formatSigned(lockedCase.delta_release_speed, 1)} mph</strong>
                <small>session means</small>
              </div>
              <div>
                <span>Matched effect</span>
                <strong>{matchedDelta}</strong>
                <small>RV / 100</small>
              </div>
              <div>
                <span>Controls</span>
                <strong>{lockedCase.n_matches}</strong>
                <small>same-family matches</small>
              </div>
            </div>
          </div>
        </section>

        <section id="methodology" className="section methodology-section">
          <div className="section-heading" data-reveal>
            <div>
              <div className="section-kicker">Methodology</div>
              <h2>Built to be challenged.</h2>
            </div>
            <p>
              ShapeShift separates intervention detection, outcome modeling, effect
              estimation, and recommendation. Each layer has a failure criterion.
            </p>
          </div>

          <div className="pipeline">
            {[
              ["01", "Ingest", "Immutable weekly Statcast Parquet with provenance and QA."],
              ["02", "Detect", "Outcome-blind physical changepoints by pitcher and pitch."],
              ["03", "Estimate", "Matched event study with not-yet-treated controls."],
              ["04", "Decide", "Keep / Reshape / Abandon under feasibility constraints."],
            ].map(([number, title, detail], index) => (
              <div
                className="pipeline-step"
                key={number}
                data-reveal
                style={{ transitionDelay: `${index * 90}ms` }}
              >
                <div className="pipeline-index">{number}</div>
                <div><h3>{title}</h3><p>{detail}</p></div>
                {index < 3 && <ArrowIcon />}
              </div>
            ))}
          </div>

          <div className="method-footer" data-reveal>
            <div>
              <span>Temporal design</span>
              <strong>
                {lockedReport.data.development_rows.toLocaleString()} train rows · 2024 threshold ·
                2025 locked
              </strong>
            </div>
            <div>
              <span>Primary estimand</span>
              <strong>Matched change in predicted RV / 100 pitches</strong>
            </div>
            <div>
              <span>Locked result</span>
              <strong>
                ATE {ate}; default Keep; Muñoz pattern De-emphasize
              </strong>
            </div>
          </div>
        </section>

        <footer>
          <div className="footer-brand">ShapeShift</div>
          <p>
            Independent public-data research. Not affiliated with Major League Baseball or
            the Boston Red Sox.
          </p>
          <a href="#decision" onClick={() => setActiveSection("decision")}>
            Back to decision ↑
          </a>
        </footer>
      </main>
    </div>
  );
}
