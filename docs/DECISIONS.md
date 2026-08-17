# Decision log

Append-only. Every choice an agent made without a human, and every choice a human made
that the spec does not already record.

Format:

## YYYY-MM-DD — <one-line decision>
**Ambiguity:** what was unclear
**Chosen:** what was done
**Reason:** why this over the alternative
**Reversible:** yes / no, and what it would cost

## 2026-08-16 — Bootstrap from setup pack inside Portfolio X-Ray folder
**Ambiguity:** SETUP says `gh repo create portfolio-xray --public --clone`; working folder was already `Portfolio X-Ray` with the pack extracted.
**Chosen:** Initialize git in the existing folder, promote setup contents to root, use GitHub repo name `portfolio-xray` when remote is created. Drop the nested `setup/` staging tree and the zip from version control after promote.
**Reason:** Avoid a second clone and duplicate trees; same machine contents either way.
**Reversible:** yes — rename folder or recreate remote; cost is a few minutes of git/gh ops.

## 2026-08-16 — Commit .gitignore with .env before API key exists
**Ambiguity:** SETUP step 2 creates .env and appends to .gitignore.
**Chosen:** Create `.gitignore` including `.env` during Step 1.
**Reason:** Fail-closed so a key can never be committed accidentally if Step 2 runs out of order.
**Reversible:** yes — no behavior change beyond earlier ignore.

## 2026-08-16 — Canonical remote is spocalypse/Portfolio-Scan
**Ambiguity:** SETUP names the repo `portfolio-xray`; Om created `Portfolio-Scan` on GitHub.
**Chosen:** Treat https://github.com/spocalypse/Portfolio-Scan as the canonical repo. Keep product name Portfolio X-Ray in docs/SPEC.
**Reason:** Remote already exists and auth works; renaming is cosmetic for v0.1.
**Reversible:** yes — rename on GitHub later; update remotes.

## 2026-08-16 — Promote contracts into Portfolio-Scan before branch protection
**Ambiguity:** Operating pack lived in the parent Portfolio X-Ray folder while GitHub clone was empty.
**Chosen:** Copy CLAUDE.md, AGENTS.md, SETUP.md, .claude, .cursor, .github, docs/*, scripts/* into Portfolio-Scan and push to main, then enable protection.
**Reason:** SETUP order — contracts on main before agents open PRs.
**Reversible:** yes.

## 2026-08-16 — Scaffold CI skips frontend/eval jobs via job-level if
**Ambiguity:** Required checks frontend / design-tokens / security must report; web/ and evals/ do not exist yet.
**Chosen:** Job-level `if: hashFiles(...) != ''` on frontend, design-tokens, and extraction-eval. No workflow `paths:` filter.
**Reason:** Skipped jobs still report and satisfy required checks; path filters can leave checks pending forever.
**Reversible:** yes — remove the `if:` once web/ and evals/ land.

## 2026-08-16 — CORRECTION: hashFiles only works on steps, not job-level if
**Ambiguity:** GitHub rejected the workflow: `Unrecognized function: 'hashFiles'` on job-level `if:` (lines 52/72/91). Jobs never started → required checks stayed "Expected — Waiting".
**Chosen:** Keep jobs always scheduled (so required checks report). Move presence guards to **step-level** `if: hashFiles(...)` with an explicit no-op success step when absent. Still no workflow `paths:` filter.
**Reason:** `hashFiles` is documented for step `if` only; job-level use invalidates the whole workflow file.
**Reversible:** yes.

## 2026-08-16 — Privacy pytest exit code 5 is success during scaffold
**Ambiguity:** CI runs `pytest -m privacy` before any privacy tests exist (exit code 5 = no tests collected).
**Chosen:** Treat exit codes 0 and 5 as pass in the privacy CI step.
**Reason:** Keeps the step wired without inventing placeholder privacy tests.
**Reversible:** yes — remove the exit-5 branch once real privacy tests exist.

## 2026-08-16 — Dependencies live in api/pyproject.toml, not requirements.txt
**Ambiguity:** Original CI pip-audit used `api/requirements.txt`, which the scaffold does not create.
**Chosen:** Editable install from `api[dev]`, then `pip-audit` against the environment (soft-fail `|| true` retained).
**Reason:** Single source of truth in pyproject; no duplicate lock file yet.
**Reversible:** yes — add a frozen requirements export later if desired.

## 2026-08-16 — uvicorn and httpx added beyond the minimal FastAPI/pydantic list
**Ambiguity:** Issue #1 named FastAPI + pydantic (+dev pytest/ruff/bandit) but `make dev` and TestClient need a server and httpx.
**Chosen:** Add `uvicorn[standard]` as a runtime dependency and `httpx` under `[dev]`.
**Reason:** `make dev` and `tests/test_health.py` would not work otherwise; logged per CLAUDE.md dependency rule.
**Reversible:** yes — swap ASGI server later with a logged reason.

## 2026-08-16 — Empty package dirs under analytics/extract/narrate with no prompts yet
**Ambiguity:** AGENTS.md forbids cloud agents from analytics and prompt paths; issue #1 asks for empty `__init__.py` package dirs only.
**Chosen:** Create empty `__init__.py` files under extract/resolve/data/analytics/narrate; do not create prompts/ yet.
**Reason:** Matches the issue carve-out (skeleton only) and SPEC §5.12 layout without touching prompt content or SPEC.
**Reversible:** yes.

## 2026-08-16 — Agent PR automation needs Pull requests write on the PAT
**Ambiguity:** Branch push succeeded; `gh pr create` returned 403 Resource not accessible by personal access token.
**Chosen:** Document required fine-grained scopes (Contents, Workflows, Pull requests, Issues, Metadata) and add `pr-opener` subagent + Cursor `open-pr` skill so agents retry after Om updates the token.
**Reason:** Branch protection + agent PRs are load-bearing; missing PR scope blocks the whole loop.
**Reversible:** yes — scopes can be narrowed later if a human opens every PR.

## 2026-08-16 — next/font/google for Inter + IBM Plex Mono (build-time self-host)
**Ambiguity:** SPEC requires self-hosted fonts; issue allows next/font if logged.
**Chosen:** Use `next/font/google` for Inter (body) and IBM Plex Mono (numerals). Next downloads and self-hosts at build time; no runtime Google Fonts CDN.
**Reason:** Matches create-next-app App Router defaults and AGENTS.md “fonts are self-hosted” without vendoring font files in-repo.
**Reversible:** yes — switch to `next/font/local` with files under `web/public/fonts/` if offline builds become a constraint.

## 2026-08-16 — Keep create-next-app web/AGENTS.md + web/CLAUDE.md
**Ambiguity:** Root already has AGENTS.md / CLAUDE.md; create-next-app 16 writes Next-specific agent notes under `web/`.
**Chosen:** Commit `web/AGENTS.md` and `web/CLAUDE.md` as generated. Repo operating contract remains root `AGENTS.md` / `CLAUDE.md`.
**Reason:** `next dev` re-creates them if removed; committing avoids perpetual dirty tree.
**Reversible:** yes — delete later if Next stops auto-writing them.

## 2026-08-16 — Type scale steps sized on 8px rhythm
**Ambiguity:** SPEC §5.11 requires five type steps but does not prescribe px sizes.
**Chosen:** `--step-1` 12px, `--step-2` 14px, `--step-3` 16px, `--step-4` 24px, `--step-5` 40px.
**Reason:** Eyebrow → body → instrument value hierarchy on an 8px grid; no sixth step.
**Reversible:** yes — adjust px values in `tokens.css` only.

## 2026-08-16 — Issue #3 branch accidentally forked from a concurrent web/ commit
**Ambiguity:** N/A — this is a process note, not a spec ambiguity. A concurrent session
shared this working directory and checked out `web/issue-2-next-tokens`, committing
`web: scaffold Next.js and design tokens` on it between two of my own git checks. My
`git checkout -b contract/issue-3-freeze-api-schema` ran while that branch was checked
out, so it silently forked from there instead of `main`.
**Chosen:** Caught it before any commit existed on the new branch (confirmed via
`git reflog`), deleted and recreated the branch cleanly off the now-fast-forwarded
`main` (which had meanwhile also gained the merged web/issue-2 PR on `origin/main`).
**Reason:** A schema-only PR must not carry an unrelated Lane B commit in its history.
**Reversible:** n/a — corrected before any commit; no history rewritten on a shared ref.

## 2026-08-16 — `fixtures/metrics.sample.json` holds the full `AnalyzeResponse`, not bare `metrics{}`
**Ambiguity:** SPEC §5.10 says only "`metrics` shape is fixed ... committed as
`fixtures/metrics.sample.json`," without saying whether the file's JSON root is the bare
`metrics` object or the full response envelope.
**Chosen:** The fixture's top level is `{metrics, findings, meta}` (`AnalyzeResponse`).
**Reason:** Lane B needs `findings` and `meta` to build the whole readout page against a
single fixture; the SPEC sentence names the artifact for the metrics shape it freezes, not
a literal restriction on the file's JSON root.
**Reversible:** yes — would require a fixture format bump and updating any Lane B code
that reads the file, logged here so that's a visible, deliberate change if it happens.

## 2026-08-16 — Pydantic schema package layout: `api/src/px/schemas/{common,extract,metrics,analyze,samples}.py`
**Ambiguity:** SPEC doesn't say where the frozen-contract models live; CLAUDE.md's lane
table doesn't call out a schemas path.
**Chosen:** New `api/src/px/schemas/` package, split one file per route plus a `common.py`
base and a `metrics.py` holding all of M1–M6 (the biggest, most load-bearing file, named to
mirror SPEC §5.5's `m1_`–`m6_` subsections for direct traceability).
**Reason:** Isolates the actual frozen contract (`metrics.py`) as the obvious single file to
diff when a change to it is proposed — which CLAUDE.md treats as an escalation, not an edit.
**Reversible:** yes — pure file reorganization, imports would need updating.

## 2026-08-16 — `SectorExposure` unifies M1 capital weight and M3 sector risk contribution
**Ambiguity:** SPEC's M1 (sector capital weight) and M3 (risk contribution aggregated by
sector) are described in separate paragraphs; nothing dictates whether they share a model.
**Chosen:** One `SectorExposure{sector, capital_weight, risk_contribution_pct}` object per
sector, not two separate lists the frontend joins by sector-name string.
**Reason:** SPEC §5.11's signature divergence bar needs both values for the same sector
side by side; a string-keyed join across two arrays is fragile and works against a frozen,
unambiguous shape.
**Reversible:** yes — would require a fixture/model split and Lane B rework.

## 2026-08-16 — `M4.naive_position_count` kept distinct from `M1.effective_position_count`
**Ambiguity:** SPEC has two different "effective count" ideas — M1's `1/HHI`
(weight-concentration based) and M4's ENB (eigenvalue/correlation based), with M4's naive
count reported "beside" ENB — risk of collapsing onto one field name.
**Chosen:** Three distinct fields: `M1.effective_position_count`, `M4.naive_position_count`,
`M4.effective_number_of_bets`. `Metrics` enforces `naive_position_count ==
len(m1_weights.position_weights)` via a cross-model validator.
**Reason:** These measure different things; conflating them would silently lose one of
SPEC's two concentration metrics.
**Reversible:** yes.

## 2026-08-16 — `FactorLoading.significant` computed deterministically and shipped as data
**Ambiguity:** SPEC's `|t|≥2` significance rule for M5 is stated as a narrative-layer rubric
("only loadings with |t|≥2 may be described as tilts"), not explicitly as a metrics field.
**Chosen:** `significant: bool` is a first-class field on `FactorLoading`, enforced by a
Pydantic validator (`significant == (abs(t_stat) >= 2)` exactly, checked at construction).
**Reason:** CLAUDE.md rule 1 — the LLM never does arithmetic, including thresholding — so
this classification must be deterministic Python under test, not left to A2's prompt.
**Reversible:** yes — would become a derived/computed property instead of a stored field.

## 2026-08-16 — No invented staleness threshold for M2 R² or M6 ETF snapshot age
**Ambiguity:** §6.7 implies low-R² betas and stale ETF snapshots should surface as flags,
but SPEC gives no numeric threshold for either, unlike M5's exact `|t|≥2` rule.
**Chosen:** Expose raw `m2_beta.r_squared` and `m6_etf_look_through.snapshot_date` only; no
`low_r_squared` or `etf_snapshot_stale` boolean invented in this schema.
**Reason:** Avoids baking an arbitrary, unlogged-by-SPEC threshold into the frozen contract;
`meta.price_data_stale` stays narrowly scoped to §5.4's literal cache-fallback behavior.
**Reversible:** yes — add a derived flag later once a threshold is specified.

## 2026-08-16 — `Severity` constrained to a 2-value enum (`info`, `notable`)
**Ambiguity:** SPEC §5.6 gives `Finding.severity` as a free field; §6.7 separately requires
severity "capped at neutral-factual" with "no alarm, no moralising."
**Chosen:** `Severity(StrEnum)` with exactly `info`/`notable` — no `warning`/`critical`/etc.
**Reason:** Enforces the no-alarm rule at the type level instead of trusting A2's prompt
discipline alone; `--alert` red stays reserved for structured hard flags elsewhere (excluded
holdings, stale data), not for finding severity.
**Reversible:** yes — widen the enum later with a logged reason if a real need appears.

## 2026-08-16 — Global `extra="forbid"` via a shared `PXBaseModel`
**Ambiguity:** CLAUDE.md rule 3 requires no currency field downstream of extraction; SPEC
doesn't prescribe how that's structurally enforced.
**Chosen:** Every model in `px/schemas/` inherits `PXBaseModel(BaseModel)` with
`model_config = ConfigDict(extra="forbid")`, not just `Holding`/`AnalyzeRequest`.
**Reason:** Fails closed on unexpected fields everywhere, not only at the one boundary
model — defense in depth for the privacy boundary and an early signal of contract drift.
**Reversible:** yes.

## 2026-08-16 — `/api/samples` maps to 3 of SPEC §5.8's 6 golden portfolios
**Ambiguity:** SPEC §5.10 says `/api/samples` returns "3 canned portfolios" without naming
them.
**Chosen:** 100% SPY; 50/50 SPY/SHV; equal-weight 10 mega-cap tech (AAPL, MSFT, GOOGL, AMZN,
NVDA, META, TSLA, AVGO, ORCL, CRM — SPEC only says "10 mega-cap tech," tickers are my
choice). The other 2 golden cases (SPY+VOO overlap, 30-day-IPO exclusion) stay test-only
fixtures for the future `analytics/` suite, not exposed via the route.
**Reason:** Chosen for demo value; gives free reuse once `analytics/` lands — these become
literal golden-portfolio test inputs for 3 of the 6 §5.8 assertions.
**Reversible:** yes — swap tickers or portfolios without a schema change.

## 2026-08-16 — `fixtures/metrics.sample.json` is script-generated, never auto-regenerated
**Ambiguity:** Issue #3 doesn't specify how the fixture file should be produced or kept
in sync with the models.
**Chosen:** `scripts/build_metrics_fixture.py` builds one validated `AnalyzeResponse`
instance and writes it via `model_dump_json`. Run manually; not wired into `make test` or
`make lint`.
**Reason:** Generating from a validated instance guarantees the fixture is numerically
self-consistent (Σw=1, ΣRC%=1, etc.), not just schema-valid; auto-regenerating on every
test run would silently defeat "this is the frozen contract, changing it is an escalation."
**Reversible:** yes — hand-edit the JSON later if the generator becomes a burden, logged if
so.

## 2026-08-16 — `ExtractResponse` carries §5.2's full field list, not just §5.10's abbreviation
**Ambiguity:** §5.10's route diagram abbreviates `/api/extract`'s response to
`{rows[], warnings[], model_used}`; §5.2 separately lists `total_value` and
`brokerage_guess` as part of the same response.
**Chosen:** `ExtractResponse` includes `total_value` and `brokerage_guess` alongside
`rows`/`warnings`/`model_used`.
**Reason:** §5.2 is the fuller, more specific spec for this route; treating it as
authoritative over the diagram's shorthand avoids losing fields issue #4's extraction
agent will need.
**Reversible:** yes.

## 2026-08-16 — GICS sector list hardcoded as a `Literal`; weights are fractions in [0,1] throughout
**Ambiguity:** SPEC references "GICS sector" and "weight" without enumerating the sector
taxonomy or stating a units convention.
**Chosen:** `GicsSector = Literal[...]` over the 11 standard GICS sectors. Every
weight/percentage-like field across the schema tree (capital weight, RC%, overlap %,
r_squared, etc.) is a fraction in [0,1], never pre-multiplied by 100.
**Reason:** The 11-sector GICS list is stable and low-risk to hardcode now; a uniform units
convention avoids a silent mismatch between, e.g., `overlap_pct` and `weight` that a
frontend could format inconsistently.
**Reversible:** yes — GICS list can be extended; units convention would need a coordinated
change across schema and Lane B if ever revisited.

## 2026-08-16 — Cross-field invariants (Σw=1, ΣRC%=1, etc.) enforced by Pydantic validators, not only by tests
**Ambiguity:** SPEC §5.8 says of ΣRC%=1 "assert this in a test"; it doesn't say whether the
model itself should also refuse to construct an inconsistent instance.
**Chosen:** `model_validator(mode="after")` on `M1Weights`, `M3RiskContribution`,
`FactorLoading`, `M5FactorTilts`, and `Metrics` enforce the sum-to-one, `effective_position_
count≈1/hhi`, `naive_position_count` consistency, and `significant==(|t|≥2)` invariants at
construction time, at the SPEC-mandated tolerances (1e-6 for the sums).
**Reason:** Stricter than the issue literally requires, but construction-time enforcement
is an earlier, stronger version of "assert this in a test" — any future code building a
`Metrics` instance (real or test) gets the same guardrail for free. Per CLAUDE.md rule 2,
these tolerances must never be loosened; a future fixture that can't satisfy one is an
escalation, not a widened assertion.
**Reversible:** yes — would need to move the checks into test-only assertions instead.

## 2026-08-16 — Static readout loads fixture via fs from repo root
**Ambiguity:** Lane B must build against `fixtures/metrics.sample.json` at repo root; Next.js package root is `web/`, and duplicating the JSON would drift from the frozen contract.
**Chosen:** Server component calls `readFileSync` on `../fixtures/metrics.sample.json` relative to `web/` cwd (`loadSampleAnalyze`). Types in `web/lib/types.ts` mirror the fixture shape only — no invented fields.
**Reason:** Single source of truth for the Day-1 contract; no copy under `web/` that can go stale; no live API.
**Reversible:** yes — switch to a path alias / `externalDir` import or a generated `web/` copy if fs-at-build becomes awkward in deploy.

## 2026-08-16 — Defer numeral count-up motion on the static readout
**Ambiguity:** SPEC §5.11 asks for one orchestrated load sequence (numerals count up once); issue #7 acceptance is field coverage + design-tokens CI.
**Chosen:** Ship a static instrument layout (divergence bars, findings, all fixture fields) without count-up animation.
**Reason:** Motion needs a client island and is not in the issue acceptance bar; keep the first product-looking screen simple. `prefers-reduced-motion` work lands with motion.
**Reversible:** yes — add a small client `CountUp` later without schema changes.

## 2026-08-16 — Un-ignore web/lib/ against root Python lib/ gitignore
**Ambiguity:** Root `.gitignore` (Python template) has bare `lib/`, which also ignores `web/lib/` where the readout helpers live.
**Chosen:** Add `!web/lib/` exception; keep helpers at `web/lib/{types,format,load-fixture}.ts`.
**Reason:** Matches Next/App Router convention (`@/lib/...`); narrower than renaming the folder.
**Reversible:** yes — rename to `web/readout/` and drop the exception if preferred.

## 2026-08-16 — Mock extract fixture until /api/extract is wired
**Ambiguity:** Issue #14 needs upload → confirm before readout, but Lane A extract (#4) is not merged; live Anthropic is out of scope.
**Chosen:** On file select, load `fixtures/extract.sample.json` (ExtractResponse shape from `api/src/px/schemas/extract.py`, including `model_used`) via the same server-side fs pattern as metrics. Image `File` stays in React state only. Confirm edits derive capital weights from market_value shares; Analyze advances to the existing metrics fixture readout (honest eyebrow). Exchange is confirm-UI-only (NYSE/NASDAQ/AMEX/Other), not an ExtractResponse field.
**Reason:** Unblocks the D3 demo path without inventing API fields or calling Anthropic; dollars never enter the readout stage.
**Reversible:** yes — swap mock load for `POST /api/extract` and fixture readout for live analyze when #4/#21 land.

## 2026-08-16 — Stub redaction notice on upload; full canvas is #10
**Ambiguity:** SPEC §6.3 lists manual redaction before upload; issue #14 marks full canvas redaction out of scope.
**Chosen:** Copy-only stub on the upload stage ("Canvas redaction lands in #10"); no canvas, no pixel burn-in.
**Reason:** Keeps #14 minimal and demo-useful without blocking on #10.
**Reversible:** yes — replace stub with canvas when #10 ships.
## 2026-08-16 — `anthropic` and `python-multipart` added as new dependencies (issue #4)
**Ambiguity:** SPEC §5.9 lists `anthropic` in the backend stack but it was never actually
added to `api/pyproject.toml`; FastAPI's multipart `UploadFile`/`File` parsing separately
requires `python-multipart` at runtime, which the scaffold also never added.
**Chosen:** Add both to `[project].dependencies` in `api/pyproject.toml`.
**Reason:** `anthropic` is the SDK the A1 agent calls Haiku/Sonnet through; `python-
multipart` is required for `POST /api/extract` to accept an uploaded image at all —
neither is optional once this issue's acceptance criteria are met.
**Reversible:** yes — swap SDKs later with a logged reason.

## 2026-08-16 — A1 escalation aggregate is `min(row.confidence)`; empty rows do not escalate
**Ambiguity:** SPEC §5.2 says "escalate to Sonnet only when self-reported confidence < 0.8
or schema validation fails," but `ExtractResponse` has no top-level confidence field —
only per-row `confidence` exists — so an aggregation rule had to be chosen.
**Chosen:** Escalate iff the minimum confidence across all rows is < 0.8 (any one
uncertain row is enough), or the model's tool output fails schema validation. A response
with zero rows has no confidence values to aggregate and is not itself an escalation
trigger — SPEC names exactly two triggers, and CLAUDE.md rule 6 says take the simpler,
literal option rather than inventing a third.
**Reason:** "Any row uncertain → get a second opinion" is the natural reading of a
per-row confidence signal; declining to invent a third trigger keeps the routing rule
exactly traceable to SPEC's two named conditions.
**Reversible:** yes — swap to a different aggregate (e.g. mean, or escalate on empty rows
too) with a logged reason if eval data (issue #6) shows it matters.

## 2026-08-16 — `model_used` is stamped by application code, never trusted from the model
**Ambiguity:** `ExtractResponse.model_used` must reflect which model actually produced
the accepted result; the model itself has no privileged way to know or honestly report
its own identity inside a tool call.
**Chosen:** The LLM's tool call target (`ExtractionPayload` in
`api/src/px/extract/payload.py`) mirrors `ExtractResponse` minus `model_used`. The agent
sets `model_used` itself to the literal id of whichever API call's output was accepted.
`ExtractionPayload.rows` reuses the frozen `ExtractRow` model directly (it has no
model-identity field to begin with), so there is no duplicate row schema to drift.
**Reason:** Keeps model self-identification out of the model's hands entirely — the same
spirit as "the LLM never does arithmetic," extended to "the LLM never asserts its own
provenance."
**Reversible:** yes.

## 2026-08-16 — Structured extraction via forced Anthropic tool-use, not freeform JSON
**Ambiguity:** SPEC §5.2 says "strict JSON, Pydantic-validated" without specifying how the
model is made to emit it.
**Chosen:** `agent.py` calls the Anthropic Messages API with a single tool
(`emit_holdings_extraction`, `tool_choice` forced) whose `input_schema` sets
`additionalProperties: false` at every level; the tool's `input` dict is then validated
against `ExtractionPayload` (which also inherits `extra="forbid"`). Any parse or
validation failure is treated identically to a low-confidence result: it triggers
escalation to Sonnet, and if Sonnet also fails, raises `ExtractionFailedError` — no
regex-scraped JSON, no partial/best-effort response.
**Reason:** Forced tool-use is materially more reliable than asking for prose JSON and
gives two independent layers (JSON Schema, then Pydantic) against a smuggled field like
an account identifier, matching CLAUDE.md's "strict Pydantic validation" requirement.
**Reversible:** yes — swap to freeform JSON parsing with a logged reason if tool-use
proves unreliable in practice.

## 2026-08-16 — Minimal server-side upload guard: magic-byte sniff + 10 MB ceiling
**Ambiguity:** SPEC §6.3's EXIF-strip/downscale/redaction/MIME-sniffing pipeline is
explicitly scoped to Lane B's client-side upload flow (issue #10, still open); nothing
says whether `POST /api/extract` itself should validate anything before spending an API
call.
**Chosen:** `main.py` sniffs the first bytes for PNG/JPEG/WEBP magic numbers (rejecting
anything else with 400) and caps the read at 10 MB (rejecting larger with 413), before
the bytes ever reach `extract_holdings`. No EXIF stripping, no downscaling, no
decompression-bomb guard — those remain issue #10's scope.
**Reason:** A boundary that accepts arbitrary bytes and hands them straight to a paid
vision API call is a needless cost/abuse surface even in a local-only prototype; the
10 MB figure is not specified anywhere in SPEC, chosen as a conservative round number
well above any realistic full-screen screenshot.
**Reversible:** yes — raise/lower the ceiling or drop the sniff once issue #10's full
client-side validation makes it redundant.

## 2026-08-16 — Extraction request logging follows the §6.6 allowlist exactly
**Ambiguity:** §6.6 specifies the allowlist (`request_id`, `duration_ms`, `model_used`,
`row_count`, `error_code`) at the repo level but no code enforced it yet.
**Chosen:** `agent.py` logs exactly those five fields via `extra=` on one `logger.info`
call per request — never the image bytes, raw_label text, or any extracted row content.
Covered by a regression test (`test_log_line_contains_only_the_allowlisted_fields`) that
inspects the actual `LogRecord`.
**Reason:** Establishes the allowlist pattern in code, not just in SPEC prose, before any
other module starts logging.
**Reversible:** yes — extend the allowlist later with a logged reason.

## 2026-08-16 — `pandas` and `pyarrow` added as new dependencies (issue #5)
**Ambiguity:** SPEC §5.3 says the symbol table is "cached as parquet"; SPEC §5.9 lists
`pandas` in the backend stack, but neither was ever added to `api/pyproject.toml`.
**Chosen:** Add both to `[project].dependencies`.
**Reason:** `pandas` is the SPEC-named data-handling library; `pyarrow` is its standard
parquet engine (pandas has no default parquet engine of its own) — required to read/
write `fixtures/symbol_table.parquet` at all. Same "pre-approved by SPEC, just not yet
declared" situation as `anthropic` was for issue #4.
**Reversible:** yes.

## 2026-08-16 — `nasdaqlisted.txt` + `otherlisted.txt` together are "the NASDAQ/NYSE
listings" SPEC §5.3 names
**Ambiguity:** SPEC says "local symbol table from public NASDAQ/NYSE listings" without
naming a specific source or file.
**Chosen:** NASDAQ Trader's public, unauthenticated symbol directory —
`nasdaqtrader.com/dynamic/SymDir/{nasdaqlisted,otherlisted}.txt` — fetched via
`scripts/build_symbol_table.py` (stdlib `urllib.request`, no new dependency for the
fetch itself) and written to `fixtures/symbol_table.parquet`: 13,111 rows (5,586
NASDAQ-listed, 5,612 flagged ETF across both files), confirmed zero ticker collisions
between the two source files. `otherlisted.txt` is taken in full (NYSE + NYSE American +
NYSE Arca + Cboe BZX + IEX), not filtered down to `Exchange=='N'` only — this pair of
files is the standard, complete public US-listed-securities directory these two
canonical filenames refer to, and SPEC's own examples elsewhere (§2 "US-listed equities
and ETFs", D2 "US-only") point at full US coverage, not literally NYSE-the-single-
exchange. Rows with `Test Issue == Y` are dropped (synthetic test symbols like ZZZZ);
no other filtering (rights/warrants/units/preferred shares stay in — SPEC doesn't ask
to exclude them, and rule 6 says take the simpler reading).
**Reason:** Network access to this exact domain was verified reachable before choosing
it; the file is free, unauthenticated, and is literally what "NASDAQ/NYSE listings"
means in practice for anyone building this kind of table.
**Reversible:** yes.

## 2026-08-16 — `fixtures/symbol_table.parquet` is script-generated, never
auto-regenerated
**Ambiguity:** Same question as `fixtures/metrics.sample.json` in issue #3 — how the
symbol table should be produced and kept in sync.
**Chosen:** `scripts/build_symbol_table.py` fetches, parses, and writes the parquet file
once; it is checked in and never re-run by `make test`/`make lint`/CI.
**Reason:** Identical reasoning to the metrics-fixture precedent: a table that changes
silently on every CI run would defeat determinism and make "resolves/doesn't resolve"
regressions invisible. Re-running the script to refresh delistings/new listings is a
deliberate, logged action.
**Reversible:** yes — re-run the script and commit the new file with a logged reason
whenever a refresh is wanted.

## 2026-08-16 — Resolver ambiguity: share-class separator variants only, never bare
concatenation
**Ambiguity:** SPEC §5.3 says ambiguous rows must "surface a dropdown... rather than
auto-resolving," without specifying what counts as ambiguous or how to detect it
against a real ~13k-row table.
**Chosen:** `resolve_holdings` in `api/src/px/resolve/resolver.py`: (1) exact
ticker match always wins outright, no further checks; (2) failing that, for a ticker
shaped like `BASE` + separator (`.`/`-`/`/`) + one letter, or a bare `BASE` alone, try
the other separators from `{'.', '-', '/'}` — deliberately **excluding** the
no-separator/concatenated form. Collect the distinct real table hits: exactly one →
resolve to it (handles a brokerage rendering `BRK.B` as `BRK-B`); two or more → excluded
with `reason="ambiguous"` and the full candidate list, never a guess (e.g. a bare `BRK`
is genuinely ambiguous between the real `BRK.A`/`BRK.B`, confirmed against the checked-
in fixture — see `tests/test_symbol_table.py`). Concatenation (no separator at all) was
tried first and reverted: against the real table, `"BRK" + <any letter>` false-
positive-matched unrelated real tickers (`BRKR`, `BRKU`, `BRKC`, `BRKL`, `BRKW`, …) —
it degenerates into blunt prefix matching, not share-class detection.
**Reason:** This is why `GOOG`/`GOOGL` (Alphabet's two real, fully independent tickers,
not a base+class-letter pair under this scheme) must never cross-match: `GOOG` and
`GOOGL` both hit the exact-match path directly and never reach variant scanning at all.
Covered explicitly in both `tests/test_resolver.py` (synthetic) and
`tests/test_symbol_table.py` (real fixture) per the acceptance criterion's "unit tests
for collision cases."
**Reversible:** yes — reintroduce concatenation with a name-similarity or confidence
gate later if eval data shows it's needed, logged if so.

## 2026-08-16 — Resolver does not renormalize weights after exclusion
**Ambiguity:** SPEC doesn't say whether the Resolver should renormalize the remaining
holdings' weights after excluding some.
**Chosen:** `ResolvedHolding.weight` is passed through unchanged from the input
`Holding.weight`.
**Reason:** `AnalyzeRequest`/`Holding` has no cross-holding sum-to-1 invariant enforced
today (only a per-field `[0,1]` bound); SPEC's M1 `w_i = mv_i / Σ mv` formula is the
Quant Engine's job (issue #11), which will naturally compute weights over whatever
holdings it actually receives. Renormalizing twice (once here, again in M1) would be
the exact double-counting bug `quant-verifier` is told to hunt for.
**Reversible:** yes — move renormalization here instead with a logged reason if M1's
implementation ends up wanting resolver-normalized input.

## 2026-08-16 — Resolver's exclusion reasons map onto `schemas.metrics.ExcludedHolding`
but aren't that type
**Ambiguity:** `api/src/px/schemas/metrics.py` already defines a frozen
`ExcludedHolding{ticker, reason: Literal["non_us_ticker","insufficient_price_history",
"resolution_failure"], detail}` from issue #3. The resolver needs its own richer
exclusion type (candidates list, raw ticker) but must not silently diverge from that
vocabulary.
**Chosen:** `resolve.ExcludedHolding.reason` is its own `Literal["not_found",
"ambiguous","non_us_suffix"]` — a different, resolver-internal type, not the frozen
schema. Documented mapping for whichever issue wires `resolve_holdings` into
`/api/analyze`: `not_found`/`ambiguous` → `resolution_failure` (with `raw_ticker`/
`candidates` folded into the frozen model's free-text `detail`); `non_us_suffix` →
`non_us_ticker`.
**Reason:** Keeps `resolve/` free of a dependency on the frozen contract schema (it
isn't itself part of §5.10's frozen API) while giving future wiring work an
already-decided, unambiguous mapping instead of re-litigating it.
**Reversible:** yes.

## 2026-08-16 — Ambiguous-row dropdown UI is out of scope for issue #5
**Ambiguity:** SPEC §5.3's "surface a dropdown in the confirm UI rather than
auto-resolving" implies an interactive disambiguation flow, but the frozen §5.10 API
contract has no dedicated resolve endpoint — only `/api/extract`, `/api/analyze`,
`/api/samples`.
**Chosen:** Build only the pure detection logic (`ExcludedHolding.reason="ambiguous"`
with a `candidates` list) in this issue. No new route, no UI wiring.
**Reason:** Adding a resolve-specific endpoint would be a change to the frozen API
contract — CLAUDE.md's escalation protocol, not something to add unilaterally inside a
`lane-a` issue scoped to "US symbol table and disambiguation" logic. Issue #5's own
acceptance criteria (exclude-and-report-by-name, unit tests for collisions) don't
require route wiring, matching the same deferred-wiring pattern already used for
`/api/analyze` itself (issues #19/#21).
**Reversible:** yes — open a `blocked-needs-human` issue proposing the contract change
if interactive disambiguation becomes a priority.

## 2026-08-17 — `yfinance==1.6.0` pinned exactly (issue #8)
**Ambiguity:** SPEC §5.9 names `yfinance` and §5.4 warns "pin the version; it breaks
without warning," without naming a specific version. Latest at build time is 1.6.0, a
major-version jump from the long-stable 0.2.x line — a real risk given the SPEC's own
warning about silent breakage.
**Chosen:** Verified 1.6.0's actual behavior directly against the live API before
committing to it (not assumed from memory): `Ticker(t).history(period="3y",
auto_adjust=True)` returns an already-adjusted `Close` column on a tz-aware
`DatetimeIndex`; `.info` has `sector`/`industry` (both `None` for ETFs, e.g. SPY); an
unresolvable ticker returns an **empty DataFrame**, not an exception. Pinned to exactly
`yfinance==1.6.0` (no `>=`) on that verified shape.
**Reason:** Given the tool to check empirically rather than guess, verifying beats
assuming — especially right after SPEC explicitly flags this exact library as prone to
undocumented breaking changes across versions.
**Reversible:** yes — bump with a logged reason (and a re-verification pass) if a newer
version is needed later.

## 2026-08-17 — Price/metadata cache is stdlib SQLite, not parquet, and gitignored
**Ambiguity:** SPEC §5.4 says "SQLite or parquet keyed by (ticker, date)"; issue #5 had
already used parquet for the symbol table, so the choice wasn't pre-set for issue #8.
**Chosen:** `api/src/px/data/cache.py` uses stdlib `sqlite3` (no new dependency) with
three tables — `prices(ticker, date, adj_close)`, `metadata(ticker, sector, industry)`,
`fetch_log(ticker, last_fetched_date)` enforcing "at most once per day." The DB file
lives at `.cache/price_cache.sqlite3`, matched by the pre-existing bare `.cache` line in
`.gitignore` (confirmed via `git check-ignore`) — never committed, unlike
`fixtures/symbol_table.parquet`.
**Reason:** The symbol table is a static, deliberately-versioned snapshot (parquet:
write-once, read-many, diffable). The price cache is the opposite — a live, per-ticker,
per-day-incrementing store — which is exactly what a keyed row-store handles naturally
(`INSERT OR REPLACE` upserts, indexed point lookups) versus rewriting a whole parquet
file on every fetch. It's also a runtime artifact, not a frozen fixture, so it shouldn't
be checked in at all.
**Reversible:** yes — swap to parquet-per-ticker with a logged reason if SQLite becomes
a bottleneck (unlikely at this data volume).

## 2026-08-17 — Retry/backoff is hand-rolled, not a new dependency
**Ambiguity:** SPEC §5.4 says "retry with backoff" without naming a library.
**Chosen:** `loader.py`'s `_fetch_with_retry` is a plain loop: up to
`DEFAULT_MAX_ATTEMPTS=3` attempts, exponential sleep
(`backoff_seconds * 2**attempt`) between them, both the attempt count and the sleep
function (`sleep_fn`) injectable so tests run instantly with zero real sleep.
**Reason:** Three attempts with exponential backoff is a handful of lines; pulling in
`tenacity` or similar for this would be a dependency with no functionality this
project actually needs beyond what's already written, against CLAUDE.md's "no new
dependency without a logged reason."
**Reversible:** yes — swap to a library later with a logged reason if retry needs grow
more elaborate (jitter, per-exception policies, etc.).

## 2026-08-17 — Total-fetch-failure fallback and the 250-day guard are two separate,
independently-testable steps
**Ambiguity:** SPEC §5.4 bundles "retry with backoff; on total failure fall back to
cache and mark stale" with the 250-day minimum-history exclusion rule in the same
paragraph, but doesn't say whether they're one mechanism or two.
**Chosen:** `fetch_ticker` (I/O: cache + retryable network fetch, always returns a
`FetchedTicker`, possibly with zero prices, and a `stale` flag) is fully separate from
`partition_by_history` (pure: `len(prices) >= 250` → included, else excluded with
`reason="insufficient_price_history"` and the actual count in `detail`). An
unresolvable ticker with no prior cache naturally flows through as a zero-price
`FetchedTicker` and gets excluded by the history guard — no special-casing, no crash,
confirmed against the real API (`ZZZNOPEXYZ` → 0 rows → excluded, not raised).
**Reason:** Same layering as resolve/'s `table.py`/`resolver.py` split (I/O boundary vs.
pure decision logic) — each half is unit-testable in isolation, and "no crash on a
missing/short-history ticker" falls out of the design rather than needing a guard
clause.
**Reversible:** yes.

## 2026-08-17 — `load_tickers` catches per-ticker exceptions so one bad ticker can't
crash a batch
**Ambiguity:** SPEC's "no crash" language is stated for the short-history case
specifically; it doesn't say what happens if an unexpected exception (not a caught
network-retry failure) occurs while processing one ticker in a batch of many.
**Chosen:** `load_tickers` wraps each `fetch_ticker` call in a broad
`except Exception`, converting any unexpected per-ticker failure into a zero-price,
`stale=True` `FetchedTicker` (which the 250-day guard then excludes) rather than
letting it abort the whole batch.
**Reason:** A portfolio of 20 holdings should not fail entirely because one ticker's
metadata call raised something `_fetch_with_retry`'s narrower exception handling didn't
anticipate — matches the spirit of "no crash," extended from the single documented case
to the batch as a whole.
**Reversible:** yes — narrow the caught exception type later with a logged reason if
this proves too permissive.
