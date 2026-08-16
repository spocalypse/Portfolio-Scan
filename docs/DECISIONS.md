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
