# Setup — building the machine

Roughly 60–75 minutes, in order. Every step ends with something you can verify, so you know
whether to continue. Stop at the first step that does not verify; a broken foundation here
costs you a day later.

---

## 1. Repo and files (10 min)

```bash
gh repo create portfolio-xray --public --clone
cd portfolio-xray
```

Copy everything from this pack into the repo root, keeping the dot-directories:

```
CLAUDE.md  AGENTS.md  SETUP.md
.claude/agents/*.md
.cursor/rules/*.mdc
.github/workflows/ci.yml  .github/ISSUE_TEMPLATE/task.yml  .github/pull_request_template.md
scripts/seed-issues.sh
docs/PROGRESS.md  docs/DECISIONS.md
```

Then drop the scope document in as `docs/SPEC.md` — it is the source of truth every one of
these files points at, so nothing works properly without it.

```bash
git add -A && git commit -m "chore: agent operating contract, rules, CI, queue" && git push
```

**Verify:** `ls -a` shows `.claude`, `.cursor`, `.github`. Dot-directories are easy to lose
when copying; if they are missing, nothing downstream works.

---

## 2. Anthropic API key and spend cap (5 min)

At console.anthropic.com: create a key, buy $10 of prepaid credits, and **set a hard monthly
spend limit of $15**. Do this before writing any code that calls the API — the cap is the
backstop that makes every other cost control optional.

```bash
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
echo ".env" >> .gitignore
```

This key is for the *app*. Your Claude Pro subscription covers Claude Code; it does not
include API access, and the two must not be confused.

**Verify:** `git status` does not list `.env`.

---

## 3. Branch protection (5 min)

Settings → Branches → add a rule for `main`:

- Require a pull request before merging
- Require status checks to pass: `backend`, `frontend`, `design-tokens`, `security`
- Do not allow bypassing

**This is the load-bearing step of the whole system.** It is what converts "agents open PRs"
from a convention into a guarantee. Without it, one `--dangerously-skip-permissions` run can
push straight to `main` at 3am.

**Verify:** try `git push` a trivial commit directly to `main`. It must be rejected.

---

## 4. Seed the queue (5 min)

```bash
gh auth login          # if you haven't
./scripts/seed-issues.sh
gh issue list --label ready
```

You should see ~22 issues across `lane-a` and `lane-b`, plus 3 gates.

**The queue is finite on purpose.** When it empties, the machine stops rather than inventing
work. New scope goes to `docs/DECISIONS.md` as a v0.2 candidate, not into the queue.

---

## 5. Claude Code, Lane A (10 min)

```bash
claude          # in the repo root, authenticate with your Pro account
```

First session, verify the contract loaded:

> Read CLAUDE.md and docs/SPEC.md. Summarise the five rules you must never break, and tell
> me which files you are forbidden from modifying.

If it cannot name the tolerance rule and the arithmetic rule, the files are not being read —
fix that before doing anything else.

Then check the subagents are registered:

```
/agents
```

You should see `quant-verifier`, `extraction-evaluator`, `red-teamer`, `docs-scribe`.

**Working pattern for every milestone:** open the issue, then

> Plan mode. Implement issue #N per docs/SPEC.md. Write the tests from §5.8 in the same
> change. Do not stop to ask; log assumptions to docs/DECISIONS.md.

Shift+Tab twice enters plan mode. Approve the plan, let it run, read the diff.

---

## 6. Cursor Cloud Agents, Lane B (10 min)

Open the repo in Cursor, confirm `.cursor/rules/` is detected in settings, then launch a
cloud agent on one `lane-b` issue from the Cursor web or desktop agent panel.

Point it at the issue by number and nothing else. The rules files carry the constraints; a
long prompt fights them.

**Verify with a throwaway task first** — have it open a PR that only edits README. Confirm:
it opened a PR (not a push to main), CI ran, and the PR template appeared. Do this before
trusting it with real work, because the failure you want to discover now is "it pushed to
main," not "it pushed to main while you were asleep."

**Cost note:** cloud agents draw your $20 Cursor credit pool. Route boilerplate to Auto mode
(free against the pool) and save frontier models for anything under `web/components/`.

---

## 7. Verify the whole loop end to end (10 min)

The one test that matters before you trust the machine overnight. Deliberately break a rule
and confirm the machine catches it:

```bash
git checkout -b test/guardrails
# in any web/ file, add: const c = "#ff00ff";
git commit -am "test: stray hex" && git push -u origin test/guardrails
gh pr create --fill
```

CI must fail on the `design-tokens` job. If it passes, your guardrails are decorative.

Delete the branch afterwards.

---

## 8. Daily rhythm

**Morning (5 min, phone):** read overnight PRs, merge the green ones, answer anything
labelled `blocked-needs-human`.

**Evening (2–3 h, laptop):** one Lane A milestone in Claude Code. Start by reading the last
three entries in `docs/PROGRESS.md`. End by having the agent append a new one.

**Before every gate:** run `quant-verifier` on quant work, `red-teamer` before G5.

**Before a long session:** check Settings → Usage. Claude Code draws from the same pool as
chat, and the weekly cap is what actually binds — pace it across the week rather than
spending it in two days.

---

## What runs unattended, and what does not

| Runs while you sleep | Needs you |
|---|---|
| GitHub Actions on every push | Merging any PR |
| Cursor Cloud Agents on `lane-b` issues | All Lane A work (analytics, prompts) |
| Nothing else | Every gate |

Claude Code is not scheduled. No cron, no headless loop against your subscription, no
`--dangerously-skip-permissions` on your real checkout. The tireless component of this
system is CI — verification, not generation. That is the part that can safely run forever.
