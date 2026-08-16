# Portfolio X-Ray — Agent Operating Contract

Analyses a brokerage screenshot and reports what the holder is actually exposed to:
portfolio beta, sector concentration, **risk** contribution vs capital weight, effective
number of bets, factor tilts, ETF overlap.

**Source of truth for all math, schemas, and design tokens: `docs/SPEC.md`.**
This file is the operating contract. Where they disagree, SPEC wins and you fix this file.

---

## Non-negotiable rules

1. **The LLM never does arithmetic.** The vision model converts pixels to structure. The
   narrative model converts a computed metrics object to English. Everything numeric
   between them is deterministic Python under test. Never ask a model to compute, estimate,
   or sanity-check a number.
2. **Never loosen a test tolerance to make a test pass.** If a golden-portfolio assertion in
   SPEC §5.8 fails, the math is wrong. Fix the math or escalate. Widening a tolerance turns
   wrong math into a green checkmark and is the single worst thing you can do to this repo.
3. **No dollar amounts past the extraction boundary.** `POST /api/analyze` accepts
   `{ticker, weight}` only. No downstream schema, log line, or frontend state may hold a
   currency value. There is an automated test for this; do not disable it.
4. **Screenshots are never persisted.** Not to disk, not to a cache, not to a log, not to a
   temp file. In-memory only, then discarded.
5. **Design tokens in SPEC §5.11 are fixed.** Five colors, five type steps, zero
   border-radius, zero shadows. No new colors. No sixth type step. No component library.
6. **Log assumptions and continue.** If this repo is ambiguous, append the assumption to
   `docs/DECISIONS.md`, take the simpler option, and keep going. Do not stop to ask unless
   the escalation protocol below applies.
7. **No new dependency without a logged reason** in `docs/DECISIONS.md`.
8. **`api/src/px/analytics/` is pure.** No network, no file I/O, no environment reads. Pure
   functions in, dataclasses out. This is what makes it testable.

## Definition of done for any task

```bash
make test          # pytest: unit + golden portfolios + privacy boundary
make eval          # extraction eval against evals/labels.json (offline fixtures)
make lint          # ruff + tsc + eslint
```

All three green, plus an entry appended to `docs/PROGRESS.md`. A task is not complete
because the code exists. It is complete because the checks pass.

## Lanes and file ownership

| Path | Owner | Notes |
|---|---|---|
| `api/src/px/analytics/` | **Lane A only** | The quant engine. Cloud agents must not touch it. |
| `api/src/px/extract/prompts/`, `narrate/prompts/` | **Lane A only** | The two LLM prompts. |
| `api/src/px/{resolve,data}/` | Lane A | |
| `web/` | Lane B | Built against `fixtures/metrics.sample.json` |
| `docs/`, `tests/` scaffolding, CI | Either | |

The API contract in SPEC §5.10 is **frozen**. If you believe it must change, that is an
escalation, not an edit — both lanes build against it.

## Escalation protocol

Stop and escalate only for these. Everything else: decide, log, continue.

- A golden-portfolio test cannot be made to pass without changing an assertion.
- The frozen API contract or metrics schema appears to need a change.
- A task requires a new secret, a paid service, or network access to a new domain.
- A privacy or safety control in SPEC §6 would have to be weakened.

To escalate: open a GitHub issue labelled `blocked-needs-human` with what you tried,
what the two options are, and your recommendation. Then move to the next queued task.

## Session start

1. Read `docs/PROGRESS.md` (last 3 entries) and `docs/DECISIONS.md`.
2. Pick the top issue labelled `lane-a` and `ready`.
3. Enter plan mode before writing code on any milestone-sized task.

## Style

- Python 3.11, type hints everywhere, `ruff` clean, docstrings on public functions only.
- Tests live next to the behaviour they prove, named for the assertion, not the function.
- Commits: `area: imperative summary` (e.g. `analytics: add risk contribution decomposition`).
- No comments explaining what the code does. Comments explain why a non-obvious choice was made.
