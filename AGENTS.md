# Portfolio X-Ray — Rules for cloud and background agents

You are running asynchronously (Cursor Cloud Agent or similar). You open pull requests.
**You never merge, and you never push to `main`.** A human reviews every PR.

Full engineering contract: `CLAUDE.md`. Math and design source of truth: `docs/SPEC.md`.
Read both before your first edit.

## Hard boundaries for this lane

**Never modify:**
- `api/src/px/analytics/**` — the quant engine
- `api/src/px/extract/prompts/**`, `api/src/px/narrate/prompts/**` — the LLM prompts
- `fixtures/metrics.sample.json` — the frozen contract both lanes build against
- `docs/SPEC.md`

If a task seems to require one of these, stop and open an issue labelled
`blocked-needs-human` instead. A PR touching those paths will be closed unread.

**Your lane:** `web/`, `docs/`, test scaffolding, CI config, dependency chores.

## Rules that apply to you specifically

1. Build the frontend against `fixtures/metrics.sample.json`. Do not call the live API
   and do not invent additional fields — if the fixture lacks something, that is a
   contract question, which is an escalation.
2. **Design tokens are fixed** (SPEC §5.11): five colors, five type steps, monospace
   tabular numerals, zero border-radius, zero shadows, no component library, no gradients.
   Adding a one-off hex value is a rejected PR.
3. **No dollar amounts anywhere in `web/`.** No currency formatting, no `$`, no
   `Intl.NumberFormat` with a currency style. The frontend receives weights only.
4. **No secrets in the frontend.** The Anthropic key is server-side only. A key reachable
   from a client component is a public key.
5. Never add analytics, telemetry, error-reporting SaaS, or a third-party font CDN.
   Fonts are self-hosted.
6. Keep PRs small and single-purpose. One issue, one PR. A PR that closes three issues
   is a PR that gets reverted as a unit.

## PR requirements

- Title: `area: imperative summary`
- Body: the issue it closes, what changed, what you decided and why, what you did not do.
- CI must be green. If CI is red, fix it in the same PR or convert to draft.
- Append your decisions to `docs/DECISIONS.md` in the same PR.

## When you have a question

Do not guess on anything in the escalation list in `CLAUDE.md`. Open an issue labelled
`blocked-needs-human`, state the two options and your recommendation, and move on to the
next `ready` issue in your lane.
