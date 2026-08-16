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
