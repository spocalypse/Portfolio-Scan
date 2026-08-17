---
name: instrument-panel-ui
description: >-
  Build or review Portfolio X-Ray web UI as a telemetry instrument panel per SPEC §5.11.
  Use when editing web/, designing readout/charts/tables, UI polish, or facelift work.
---

# Instrument panel UI (Portfolio X-Ray)

## Source of truth

1. `docs/SPEC.md` §5.11
2. `docs/UI-REVAMP-PLAN.md`
3. This skill

## Hard bans

No hex outside `tokens.css`; no border-radius/box-shadow/gradients; no component libraries; no currency; no sixth type step; motion = one numeral count-up only.

## Tokens

`--void` · `--panel` · `--rule` · `--text` · `--muted` · `--capital` · `--risk` · `--alert`  
Type `--step-1`…`--step-5`. Numerals monospace tabular.

## Charts

Hand-rolled SVG: capital = `--capital`, risk = `--risk`, never color-only (always label). HTML `<table>` with tabular nums. Prefer no chart dependency.
