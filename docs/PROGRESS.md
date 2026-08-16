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
