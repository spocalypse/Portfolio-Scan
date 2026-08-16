---
name: open-pr
description: >-
  Open or finish a GitHub pull request for the current Portfolio-Scan branch using gh.
  Use when the user asks to open a PR, create a pull request, finish issue delivery, or
  when gh pr create previously failed on PAT scopes. Never merge; never push to main.
---

# Open PR (Portfolio-Scan)

## PAT scopes (required for automation)

Fine-grained token for `spocalypse/Portfolio-Scan` must include:

| Permission | Access | Why |
|---|---|---|
| Contents | Read and write | push branches |
| Workflows | Read and write | push `.github/workflows/*` |
| Pull requests | Read and write | `gh pr create` |
| Issues | Read and write | seed/close issues |
| Metadata | Read | required by GitHub |

If `gh pr create` returns 403, tell Om to update the token and re-auth — do not paste tokens into chat.

Re-auth:

```bash
gh auth logout
gh auth login
# GitHub.com → HTTPS → Y → paste token
```

## Procedure

1. `git branch --show-current` — abort if `main`.
2. `git status` — commit only if Om asked; otherwise push existing commits.
3. `git push -u origin HEAD`
4. `gh pr create` with title `area: imperative summary` and body following `.github/pull_request_template.md`, including `Closes #N` when applicable.
5. Return the PR URL. Note which CI jobs should run vs skip for this repo state.

## Hard rules

- Never push or merge to `main`.
- Never force-push unless Om explicitly requests it.
- Never put secrets in the PR body.
- Prefer invoking Claude Code subagent `pr-opener` when working inside `claude` for the same task.
