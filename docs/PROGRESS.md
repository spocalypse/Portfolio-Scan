# Progress log

Append-only. One entry per milestone. Never rewrite an earlier entry.

Format:

## YYYY-MM-DD — <milestone>
**Built:** what changed
**Tests:** `make test` / `make eval` results, including numbers
**Assumptions logged:** links to DECISIONS.md entries
**Not done:** what was left, and why

## 2026-08-16 — Day 0 setup: local machine contracts
**Built:** Promoted operating pack to repo root (CLAUDE.md, AGENTS.md, SETUP.md, .claude/agents, .cursor/rules, .github CI/templates, scripts/seed-issues.sh). Copied scope to docs/SPEC.md. Local git init on main with initial commit.
**Tests:** N/A (no api/web yet). Structural verify: `.claude`, `.cursor`, `.github`, `docs/SPEC.md` present.
**Assumptions logged:** bootstrap folder choice; early .gitignore for .env
**Not done:** GitHub remote + push (needs `gh auth login`); Anthropic key/spend cap; branch protection; issue seed; Claude Code contract check; Lane B smoke; design-token guardrail PR.

## 2026-08-16 — Day 0: Portfolio-Scan receives the operating machine
**Built:** Copied agent contracts, Cursor rules, Claude subagents, CI, issue templates, seed script, and docs/SPEC.md into spocalypse/Portfolio-Scan. GitHub auth working as spocalypse.
**Tests:** Structural verify for `.claude`, `.cursor`, `.github`, `docs/SPEC.md`.
**Assumptions logged:** repo name Portfolio-Scan; contracts promoted before branch protection.
**Not done:** Anthropic prepaid key + $15 cap; Claude Code contract check; Lane B smoke PR; design-token guardrail PR (needs web/ scaffold).

## 2026-08-16 — Issue #1: api scaffold + CI guards
**Built:** `api/` package (FastAPI `/health`), empty `px/{extract,resolve,data,analytics,narrate}` packages, `tests/test_health.py`, Makefile (`install`/`test`/`eval`/`lint`/`dev`), `.env.example`, CI job-level skips for missing web/evals, privacy exit-5 pass, pip-audit via pyproject install.
**Tests:** `make test` — 1 passed (`test_health_returns_ok`); `make lint` — ruff clean; `make eval` — skipped (no evals/); privacy marker — exit 5 treated as pass in CI.
**Assumptions logged:** CI job-level if; privacy exit 5; pyproject vs requirements.txt; uvicorn/httpx; empty package carve-out.
**Not done:** web/ scaffold (issue #2); evals harness; real privacy tests; Anthropic `.env` key.

## 2026-08-16 — Issue #2: Next.js scaffold + design tokens
**Built:** `web/` via create-next-app (App Router, TypeScript, Tailwind, ESLint, no src, `@/*`, npm). `web/styles/tokens.css` with SPEC §5.11 palette + five type steps. Inter + IBM Plex Mono via `next/font/google`. Blank void page showing type scale + empty-state invite.
**Tests:** `cd web && npm run build` — pass; `npx tsc --noEmit` — pass; `npm run lint` — pass; `make lint` — ruff + web tsc/eslint pass.
**Assumptions logged:** next/font/google self-host; keep web/AGENTS.md; type step px sizes.
**Not done:** Fixture-driven UI (Day 1); upload/redaction; wiring to live API.

## 2026-08-16 — Issue #3: freeze API contract (Pydantic models + metrics fixture)
**Built:** `api/src/px/schemas/{common,extract,metrics,analyze,samples}.py` — Pydantic v2
models for all three §5.10 routes, transcribing §5.2 (extraction), §5.5 M1–M6 (metrics,
with cross-field invariants enforced via `model_validator`), §5.6 (findings), and §6.2
(weight-only `Holding{ticker, weight}`). `scripts/build_metrics_fixture.py` generates
`fixtures/metrics.sample.json` from a validated, internally-consistent `AnalyzeResponse`
instance (10 holdings across 6 sectors, 2 ETFs with pairwise overlap and look-through, one
excluded holding, both significant/insignificant factor-loading states, 5 findings).
Extended `make lint`/CI to cover `scripts/`. Route handlers in `main.py` intentionally left
as a stub — out of scope, wiring lands with issues #4/#19/#21.
**Tests:** `make test` — 57 passed (was 1: `test_health_returns_ok`); new coverage across
`test_extract_schema.py`, `test_metrics_schema.py`, `test_analyze_request_schema.py`,
`test_samples_schema.py`, `test_fixture_contract.py`, and `test_privacy_boundary.py` (18
tests under `pytest -m privacy`, the marker's first real collection — retires the "exit 5 =
pass" CI carve-out from 2026-08-16, though that branch is left in place since 0 and 5 both
still exit 0). `make lint` — ruff clean (api, tests, scripts) + web tsc/eslint pass. `make
eval` — skipped, no `evals/` yet.
**Assumptions logged:** 16 entries in `docs/DECISIONS.md` dated 2026-08-16, covering: a
mid-session branch mis-fork onto a concurrently-committed `web/` branch (caught via
`git reflog`, corrected before any commit existed); fixture holds full `AnalyzeResponse`
not bare `metrics{}`; schema package layout; `SectorExposure` unifying M1/M3 per sector;
`naive_position_count` kept distinct from `effective_position_count`; `significant`
computed deterministically; no invented staleness thresholds; 2-value `Severity` enum;
global `extra="forbid"`; `/api/samples` mapped to 3 of 6 §5.8 golden portfolios; script-
generated fixture; `ExtractResponse`'s full §5.2 field list; hardcoded GICS list and
uniform [0,1] weight units; construction-time invariant enforcement.
**Not done:** FastAPI route wiring (issues #4, #19, #21); the full D9 privacy suite with a
live-run log grep (issue #9) — this issue's privacy test is a structural/model-level proof
only, not a substitute.

## 2026-08-16 — Issue #7: web static readout against metrics fixture
**Built:** Replaced the Day-0 type-scale void page with a full instrument readout driven by `fixtures/metrics.sample.json` (no API). Sections: headline instruments (ENB, beta, vol, HHI), findings list, sector capital-vs-risk divergence bars, top concentration, position weights, risk contribution table, factor tilts, ETF look-through, excluded holdings (alert), meta strip, educational disclaimer. Helpers under `web/lib/` + `DivergenceBar`.
**Tests:** `cd web && npm run build` pass; `npx tsc --noEmit` pass; `npm run lint` pass; design-token greps (no stray hex / radius-shadow / currency) pass against `web/` source.
**Assumptions logged:** fs load of root fixture; defer count-up motion.
**Not done:** Live API wiring; upload/redaction; numeral count-up motion; client confirm-and-edit table.

## 2026-08-16 — Issue #14: upload + confirm-and-edit before readout
**Built:** Client stage flow upload → confirm → readout. `UploadDropzone`, `ConfirmHoldingsTable` (editable ticker/qty/value, derived weight, confidence, exchange dropdown, remove row, warnings), `InstrumentReadout` extracted from the static page, `AppShell` orchestrator. Mock `fixtures/extract.sample.json` (clear + confidence:0 rows). Image in React state only; Analyze still shows metrics fixture with honest notice. Redaction stubbed to #10.
**Tests:** `cd web && npm run build` pass; `npx tsc --noEmit` pass; `npm run lint` pass; design-token greps (no stray hex / radius-shadow / currency) pass against `web/` source.
**Assumptions logged:** mock extract until /api/extract; redaction stub #10.
**Not done:** Live extract/analyze; canvas redaction (#10); numeral count-up.

## 2026-08-16 — Issue #4: A1 extraction agent, schema, confidence handling
**Built:** `api/src/px/extract/{agent.py,payload.py,prompts/a1_extraction.py}` — the A1
extraction agent. Haiku (`claude-haiku-4-5-20251001`) is called first via a forced
Anthropic tool-use call (`emit_holdings_extraction`); escalates to Sonnet
(`claude-sonnet-5`) iff the minimum row confidence is < 0.8 or the tool output fails
schema validation (JSON Schema `additionalProperties: false` + Pydantic `extra="forbid"`,
two layers). `model_used` is stamped by application code from the call that actually
succeeded, never read from the model. If both models fail schema validation,
`ExtractionFailedError` is raised — no fallback fabrication. Wired `POST /api/extract` in
`main.py` (multipart upload, magic-byte + 10 MB guard, `Depends`-injected Anthropic
client so tests never construct a real one). Extended `test_extract_schema.py` with an
account-identifier field-set regression. Added `tests/conftest.py`'s
`FakeAnthropicClient` shared by the new `test_extract_agent.py` (routing/escalation/
logging, 8 tests) and `test_extract_route.py` (route shape/size/content-type/502, 4
tests).
**Tests:** `make test` — 70 passed (was 57). `make lint` — ruff clean (api, tests,
scripts) + web tsc/eslint pass. `make eval` — skipped, `evals/` still not present (owned
by issue #6, confirmed out of scope for this issue). Manual smoke check: one real
Haiku call via `.env`'s key against a 1x1 PNG (not committed) — returned zero rows with
an honest warning rather than fabricating holdings, confirming the tool-use → Pydantic →
`ExtractResponse` path works end to end against the live API, not just mocks.
**Assumptions logged:** 6 entries in `docs/DECISIONS.md` dated 2026-08-16 — new deps
(`anthropic`, `python-multipart`); escalation aggregate is `min(row.confidence)` with
empty rows not escalating; `model_used` stamped by code not the model, plus reusing
`ExtractRow` directly in the internal payload; forced tool-use over freeform JSON; 10 MB/
magic-byte upload guard scoped narrower than issue #10's full client-side pipeline;
§6.6 logging allowlist enforced in code with a regression test.
**Not done:** The eval harness and 12 labelled synthetic screenshots (issue #6) — this
issue's tests all mock the Anthropic client per CI's offline-only policy, so extraction
*accuracy* (ticker F1, weight MAE, hallucination rate) is unmeasured until #6 lands.
Resolver-side ticker whitelist validation (issue #5) is separate and unbuilt; A1's
"never infer an unseen ticker" rule is prompt-level only, as SPEC frames it.

## 2026-08-16 — Issue #5: US symbol resolver
**Built:** `api/src/px/resolve/{table.py,resolver.py}`. `table.py` is the sole I/O
boundary — `load_symbol_table()` reads `fixtures/symbol_table.parquet` via pandas into a
plain `dict[str, SymbolEntry]`. `resolver.py` is pure (no I/O, no network):
`resolve_holdings(holdings, table)` resolves each `{ticker, weight}` against the table —
exact match wins outright; failing that, share-class separator variants (`.`/`-`/`/`,
deliberately excluding bare concatenation, which false-positive-matched unrelated real
tickers like BRKR/BRKU against the live table) collapse brokerage-specific renderings
(`BRK-B` → `BRK.B`) to one candidate, or flag `ambiguous` with the full candidate list
when ≥2 distinct tickers match (e.g. bare `BRK` between real `BRK.A`/`BRK.B`) — never a
guess. A small explicit non-US suffix list (`.TO`, `.L`, `.AX`, …) gets its own
`non_us_suffix` reason ahead of table lookup. Everything else unresolved is
`not_found`. Weights pass through unchanged, no renormalization. `scripts/
build_symbol_table.py` fetches NASDAQ Trader's `nasdaqlisted.txt` + `otherlisted.txt`
(stdlib `urllib.request`, no new dependency for the fetch) and writes the checked-in
`fixtures/symbol_table.parquet` — run once for real this session: 13,111 rows (5,586
NASDAQ, 5,612 flagged ETF across both files), zero cross-file ticker collisions.
**Tests:** `make test` — 89 passed (was 70): `test_resolver.py` (12 tests, synthetic
tables — exact match, case/whitespace, ETF flag and weight passthrough, share-class
variant resolution, 2-way and 3-way ambiguity, exact-match short-circuiting, non-US
suffix, mixed-batch ordering) and `test_symbol_table.py` (7 tests, real checked-in
fixture, offline — includes the two collision cases named in the issue: bare `BRK`
ambiguous between real `BRK.A`/`BRK.B`, and real `GOOG`/`GOOGL` proven to never
cross-match). `make lint` — ruff clean (api, tests, scripts) + web tsc/eslint pass.
`make eval` — unaffected no-op, `evals/` still owned by issue #6.
**Assumptions logged:** 7 entries in `docs/DECISIONS.md` dated 2026-08-16 — new deps
(`pandas`, `pyarrow`); `nasdaqlisted.txt`+`otherlisted.txt` together as the literal
SPEC-named source, unfiltered beyond `Test Issue`; script-generated non-auto-
regenerated fixture (same precedent as the metrics fixture); the separator-only (no
concatenation) ambiguity mechanism and why, with the BRK/GOOG reasoning; no weight
renormalization (deferred to M1, issue #11); resolver's own exclusion-reason vocabulary
and its documented mapping onto the frozen `schemas.metrics.ExcludedHolding.reason`;
ambiguous-row dropdown UI wiring deferred (no resolve endpoint in the frozen §5.10
contract — a contract change is an escalation, not this issue's call to make).
**Not done:** No `/api/analyze` route wiring — this issue is scoped to the pure
`resolve/` module only, per its own acceptance criteria; wiring lands with whichever
issue builds `/api/analyze` (#19/#21). No interactive disambiguation UI/endpoint for the
`ambiguous` case — logged as a deferred contract question, not silently dropped.

## 2026-08-17 — Issue #12: analytics M2 portfolio beta with R²
**Built:** `api/src/px/analytics/{returns.py,m2.py}` — pure, no I/O, no network.
`returns.py` (new shared infrastructure, reused by M3-M5 as they land): `simple_returns`
(pct-change on a sorted `(date, price)` series) and `align_returns` (inner-joins
multiple tickers' return series onto their common dates, so a holiday gap or late
listing never desyncs the matrix). `m2.py`: `compute_portfolio_returns` (`r_p,t =
Σ w_i · r_i,t` via a `numpy` weighted matrix product) and `compute_beta` (`β =
cov(r_p, r_m) / var(r_m)`, `R² = corr(r_p, r_m)²` — the closed-form identity for
simple OLS R², not a full regression).
**Tests:** `make test` — 112 passed (was 103): `test_returns.py` (4 tests) and
`test_m2.py` (5 tests — 100% SPY β=1.0 exactly + R²≥0.98, 50/50 SPY/SHV β=0.5 exactly
via a zero-variance synthetic SHV proxy, uncorrelated series give R²<0.05, weighted-sum
correctness, an inverse-scaled series gives β=-1.0 as a sign sanity check). All golden
tests use seeded synthetic return series, not live data — same offline-only testing
discipline as every other module this session. `make lint` — ruff clean (api, tests,
scripts) + web tsc/eslint pass. `make eval` — unaffected no-op. Manual smoke check
against the live API (yfinance called directly, bypassing the not-yet-merged `data/`
module): real SPY vs itself → β=1.0, R²=1.0 exactly; real AAPL vs SPY over 752 aligned
trading days → β≈1.08, R²≈0.38 — both realistic, confirming the formulas and the
`align_returns` date-join work correctly end to end against real market data.
**Assumptions logged:** 4 entries in `docs/DECISIONS.md` dated 2026-08-17 —
`returns.py` built now as shared M2-M5 infrastructure, decoupled from `data/`'s
`PricePoint` type; `numpy` promoted from transitive to an explicit declared dependency;
closed-form `cov`/`corrcoef` chosen over `statsmodels.OLS` for M2 specifically (M5 will
need the latter); golden-portfolio tests use synthetic series rather than depending on
issue #8's merge order, with live-data validation done manually instead.
**Not done:** No wiring of M2's output into the frozen `Metrics`/`M2Beta` Pydantic
object — same deferred-assembly reasoning as M1. No use of the real cached price data
from issue #8 in the automated suite (by design — see decisions).

