#!/usr/bin/env bash
# Seeds the task queue from docs/SPEC.md §8. Requires the GitHub CLI (`gh auth login`).
# Idempotent-ish: re-running creates duplicates, so run once.
set -euo pipefail

echo "Creating labels..."
gh label create lane-a              --color 1D76DB --description "Interactive, Claude Code" --force
gh label create lane-b              --color 0E8A16 --description "Cloud agent, PR only"     --force
gh label create ready               --color FBCA04 --description "Unblocked, pick me up"    --force
gh label create blocked-needs-human --color D93F0B --description "Agent escalation"         --force
gh label create gate                --color 5319E7 --description "Review checkpoint"        --force

new() { # new <labels> <title> <body>
  gh issue create --label "$1" --title "$2" --body "$3"
}

echo "Seeding queue..."

# ---- Day 0 ----
new "lane-a,ready" "scaffold: repo, Makefile, CI, docs skeleton" \
"Create api/ and web/ package skeletons, Makefile with test/eval/lint/dev targets, docs/{DECISIONS,PROGRESS}.md.

Acceptance:
- \`make lint\` and \`make test\` run and exit 0 on an empty suite
- CI green on the first PR

Out of scope: any feature code."

new "lane-b,ready" "web: Next.js scaffold and design tokens" \
"Next.js App Router + TypeScript + Tailwind. Implement SPEC §5.11 tokens in web/styles/tokens.css. Self-host fonts.

Acceptance:
- \`npm run build\` passes
- design-tokens CI job green
- a blank page renders on --void with correct type scale

Out of scope: components, layout, any data."

# ---- Day 1 ----
new "lane-a,ready" "contract: freeze API shape and metrics fixture" \
"Write fixtures/metrics.sample.json covering every field in SPEC §5.10 with realistic values. Define Pydantic models for the three routes.

Acceptance:
- fixture validates against the models
- both lanes can build against it

This is the frozen contract. Changing it later is an escalation."

new "lane-a,ready" "extract: A1 vision agent, schema, confidence handling" \
"Implement extraction per SPEC §5.2. Haiku first, escalate to Sonnet on confidence < 0.8 or schema failure. Log which model handled the request.

Acceptance:
- strict Pydantic validation
- ambiguous rows emit confidence 0.0, never a guess
- no field exists for account identifiers"

new "lane-a,ready" "resolve: US symbol table and disambiguation" \
"Build the local NASDAQ/NYSE symbol table (parquet), ETF flagging, ambiguity surfacing per SPEC §5.3.

Acceptance:
- a ticker absent from the table is excluded and reported by name, never silently dropped
- unit tests for collision cases"

new "lane-a,ready" "evals: 12 synthetic screenshots and the eval harness" \
"Build evals/run_eval.py with --offline mode and recorded fixtures. 12 synthetic screenshots across 4 brokerage layouts. labels.json must declare synthetic: true.

Acceptance:
- ticker F1, weight MAE, hallucination count reported per layout
- exits 1 on regression
- runs in CI with no API key

NEVER commit a real account screenshot."

new "lane-b,ready" "web: static readout page against the fixture" \
"Render the full metrics page from fixtures/metrics.sample.json. No API calls.

Acceptance: page renders every field in the fixture; design-tokens CI green."

# ---- Day 2 ----
new "lane-a,ready" "data: yfinance layer with cache and history guard" \
"Per SPEC §5.4. Pinned version, retry with backoff, SQLite/parquet cache, 250-day minimum with explicit exclusion flagging.

Acceptance: second fetch of the same ticker hits cache; short-history holdings excluded and flagged, no crash."

new "lane-a,ready" "privacy: enforce the weight-only boundary (D9)" \
"Dollar values are discarded the moment weights are computed. Downstream schemas carry {ticker, weight} only. Allowlist logging per SPEC §6.6.

Acceptance:
- \`pytest -m privacy\` proves no currency field exists downstream
- grep of logs after a full run finds no dollar figure"

new "lane-b,ready" "web: client-side redaction, EXIF strip, downscale" \
"Per SPEC §6.3. Canvas re-encode drops EXIF; user drags black boxes burned into the canvas before upload; downscale to ~1600px long edge; MIME sniffing on bytes.

Acceptance: redacted pixels are absent from the uploaded blob (test with a byte-level assertion), not merely covered in the UI."

# ---- Day 3 ----
new "lane-a,ready" "analytics: M1 weights, sectors, HHI" \
"SPEC §5.5 M1. Pure functions, no I/O.

Acceptance: Σw = 1.0 ± 1e-6; golden tests for sector aggregation."

new "lane-a,ready" "analytics: M2 portfolio beta with R²" \
"SPEC §5.5 M2.

Acceptance: 100% SPY → β = 1.00 ± 0.02, R² ≥ 0.98; 50/50 SPY/SHV → β ≈ 0.5 ± 0.05."

new "lane-a,ready" "analytics: M3 risk contribution decomposition" \
"SPEC §5.5 M3 — the headline metric.

Acceptance: Σ RC% = 1.0 ± 1e-6 for every golden portfolio; equal-weight mega-cap tech shows tech RC% > tech dollar weight."

new "lane-b,ready" "web: upload and confirm-and-edit table" \
"Editable holdings table with per-row confidence, exchange dropdown for ambiguous rows, exclusion notices.

Acceptance: every extracted row is correctable before analysis (D3)."

# ---- Day 4 ----
new "lane-a,ready" "analytics: M4 effective number of bets (PCA)" \
"SPEC §5.5 M4, entropy-based ENB on the correlation matrix.

Acceptance: 100% SPY → ENB ≈ 1.0 ± 0.1; SPY+VOO 50/50 → ENB ≈ 1."

new "lane-a,ready" "analytics: M5 factor tilts with significance" \
"FF5 + momentum from the Ken French library, cached locally.

Acceptance: loadings carry t-stats; only |t| ≥ 2 may be labelled a tilt."

new "lane-a,ready" "analytics: M6 ETF look-through overlap" \
"Static top-holdings snapshot for ~30 US ETFs with snapshot_date.

Acceptance: SPY + VOO 50/50 → overlap ≥ 95%; snapshot date surfaced in the payload."

new "lane-b,ready" "web: divergence bar and findings panel" \
"The signature element (SPEC §5.11): capital weight in --capital above, risk contribution in --risk below, delta filled. Plus the findings list and the one-time count-up load sequence.

Acceptance: fill vanishes when the two align; prefers-reduced-motion respected."

# ---- Day 5 ----
new "lane-a,ready" "narrate: A2 findings agent with rubric" \
"SPEC §5.6. Sonnet, metrics JSON only as input. Descriptive never prescriptive; insignificant loadings called insignificant.

Acceptance: 20 sample runs contain no buy/sell/trim language."

new "lane-a,ready" "narrate: numeric validator and template fallback" \
"SPEC §5.7. Every numeral in the narrative must exist in the metrics JSON within rounding tolerance. One regeneration, then template fallback.

Acceptance: 100% pass over 20 runs (D5); an injected wrong number is caught."

new "lane-a,ready" "wire: frontend to live API end to end" \
"Replace the fixture with live calls. \`make dev\` starts both processes.

Acceptance: screenshot → result in under 30s warm (D6)."

# ---- Day 6 ----
new "lane-a,ready" "security: red-team suite in CI" \
"Standing adversarial suite per SPEC §6.4 — injection, fabrication, edge portfolios, privacy leaks.

Acceptance: all cases fail closed (D10); suite runs with the eval harness."

new "lane-b,ready" "docs: the four privacy artifacts" \
"PRIVACY.md, DATA-FLOW.md, THREAT-MODEL.md, OWASP-LLM.md per SPEC §6.8.

Acceptance: THREAT-MODEL.md has a non-empty Accepted risks section; the word 'compliant' appears nowhere; Anthropic retention claims dated and verified."

new "lane-b,ready" "web: design polish pass" \
"Spacing rhythm, focus states, contrast, 375px, empty and error states per SPEC §5.11 copy rules.

Acceptance: design-tokens CI green; keyboard-only walkthrough works."

# ---- Gates ----
new "gate" "G3: quant engine review" "All SPEC §5.8 golden tests green. Run quant-verifier before closing."
new "gate" "G4: narrative and validator review" "3 sample outputs + validator pass rate."
new "gate" "G5: demo recording, red-team and privacy artifacts" "D7, D10, D11."

echo "Done. Review the queue: gh issue list --label ready"
