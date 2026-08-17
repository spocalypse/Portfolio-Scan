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
