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

## 2026-08-16 — Issue #10: client-side redaction, EXIF strip, downscale
**Built:** `web/lib/image-prepare.ts` (MIME sniff matching API magic bytes, 10 MB
ceiling, 40e6 decoded-pixel guard, long-edge 1600 downscale, `burnRedactionRects` that
writes opaque black into the RGBA buffer, `prepareScreenshot` canvas re-encode to JPEG).
`web/components/RedactStage.tsx` — drag black boxes in natural-image coordinates, undo/
clear, Continue prepares the blob in memory. `AppShell` stage order is now
upload → redact → confirm → readout. Upload copy no longer stubs #10. Frontend CI Node
22 + `npm test`; `make lint` runs the same image-prepare unit tests.
**Tests:** `make test` — 89 passed (api unchanged). `cd web && npm test` — 6 passed,
including byte-level assertion that burned rect samples are `(0,0,0,255)` and neighbors
unchanged. `make lint` — ruff + tsc + eslint + web unit tests clean. `make eval` —
unaffected no-op.
**Assumptions logged:** 3 entries in `docs/DECISIONS.md` dated 2026-08-16 — canvas JPEG
with no new npm deps; Node strip-types tests + CI Node 22; redact as its own AppShell
stage (prepare always runs; live extract still #21).
**Not done:** Live `POST /api/extract` upload of the prepared blob (#21). Server-side
EXIF/downscale (still client-only per SPEC §6.3). Interactive resolve UI for ambiguous
tickers.

## 2026-08-17 — Issue #8: yfinance data layer with cache and history guard
**Built:** `api/src/px/data/{cache.py,source.py,loader.py}`. `cache.py` is the sole I/O
boundary — stdlib `sqlite3` (no new dependency) at `.cache/price_cache.sqlite3`
(gitignored), three tables: `prices(ticker, date, adj_close)`,
`metadata(ticker, sector, industry)`, `fetch_log(ticker, last_fetched_date)` enforcing
"fetched at most once per day." `source.py` wraps `yfinance==1.6.0` behind a `PriceSource`
protocol (verified live against the real API before writing it: `history(period="3y",
auto_adjust=True)` gives an already-adjusted `Close` column; `.info` sector/industry are
`None` for ETFs; an unresolvable ticker returns an empty DataFrame, not an exception).
`loader.py` is the orchestration layer, split into an I/O half and a pure half like
`resolve/`'s `table.py`/`resolver.py`: `fetch_ticker` checks the once-per-day cache
first, else retries the network fetch up to 3× with hand-rolled exponential backoff
(`sleep_fn` injectable for instant tests), and on total failure falls back to whatever
is cached with `stale=True`; `partition_by_history` is a separate pure function
excluding any ticker with fewer than 250 trading days (`reason=
"insufficient_price_history"`, actual count in `detail`) — an unresolvable ticker with
no prior cache flows through as zero prices and gets excluded here, never crashes.
**Tests:** `make test` — 106 passed (was 89): `test_data_cache.py` (9 tests — round-
trip, upsert-replaces, once-per-day marking, per-ticker isolation) and
`test_data_loader.py` (10 tests — fresh fetch, second-fetch-same-day cache hit
confirmed via call count, next-day refetch, retry-then-succeed with backoff values
asserted, total-failure-falls-back-to-cache-stale, total-failure-no-cache-returns-empty-
no-crash, batch never raises even with a pathological ticker, 250-day boundary
inclusive/exclusive). `make lint` — ruff clean (api, tests, scripts) + web tsc/eslint
pass. `make eval` — unaffected no-op. Manual smoke check against the live API (not part
of the suite): `AAPL` → 753 real trading days, second same-day fetch confirmed cache-
served, `SPY` → ETF with null sector/industry, `ZZZNOPEXYZ` → 0 rows, excluded, no
crash — matches automated coverage exactly.
**Assumptions logged:** 5 entries in `docs/DECISIONS.md` dated 2026-08-17 —
`yfinance==1.6.0` pinned after direct live verification (not assumed from memory, given
SPEC's own warning about this exact library breaking silently across versions); SQLite
over parquet for the cache and why (live incrementing row-store vs. static snapshot),
gitignored via the pre-existing bare `.cache` pattern (confirmed with `git check-
ignore`); hand-rolled retry/backoff instead of a new dependency; the fetch/cache layer
and the 250-day guard kept as two separate, independently-testable steps; `load_tickers`
catches per-ticker exceptions so one bad ticker can't crash a batch.
**Not done:** No wiring into `/api/analyze` or `Meta.price_data_stale`/
`price_data_as_of` — this issue is scoped to the pure `data/` module only, per its own
acceptance criteria; per-response staleness/as-of aggregation across multiple tickers is
a decision for whichever issue wires this in. Sector/industry metadata is fetched and
cached but not yet consumed by anything (M1's GICS sector grouping is issue #11).


## 2026-08-16 — UI revamp Phase 1: instrument readout charts + holdings table
**Built:** `CountUp` (one-shot numeral spin-up, respects `prefers-reduced-motion`);
`SectorDualBarChart` SVG (capital vs risk, sorted by |Δ|); `HoldingsTable` +
`buildHoldingsRows` (ticker/sector/capital/risk/Δ); elevated `DivergenceBar` `lg` for
largest sector divergence; `InstrumentReadout` re-ordered (primary finding → headline
CountUp → sector instrument → holdings table → remaining panels); AppShell max-width
1040px; plan/skill/subagent stubs under `docs/UI-REVAMP-PLAN.md`,
`.cursor/skills/instrument-panel-ui/`, `.claude/agents/ui-instrument-reviewer.md`.
**Tests:** `make test` — 106 passed. `cd web && npm test` — 7 passed (image-prepare +
holdings join). `make lint` — ruff + tsc + eslint + web tests clean. `npm run build` —
pass. Design-token greps clean.
**Assumptions logged:** Phase 1 inside §5.11 / SVG-only; CountUp rAF deferral for lint.
**Not done:** Phase 2 factor-tilt chart / ETF table polish; Phase 3 upload-stage polish;
live analyze wiring (#21).
