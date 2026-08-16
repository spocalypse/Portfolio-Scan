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
