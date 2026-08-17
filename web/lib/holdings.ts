import type { PositionWeight, RiskContribution } from "@/lib/types";

export type HoldingsRow = {
  ticker: string;
  sector: string;
  capital_weight: number;
  risk_contribution_pct: number;
  delta: number;
};

export function buildHoldingsRows(
  positions: PositionWeight[],
  contributions: RiskContribution[],
): HoldingsRow[] {
  const rcByTicker = new Map(contributions.map((c) => [c.ticker, c.rc_pct]));
  return positions
    .map((p) => {
      const rc = rcByTicker.get(p.ticker) ?? 0;
      return {
        ticker: p.ticker,
        sector: p.sector,
        capital_weight: p.capital_weight,
        risk_contribution_pct: rc,
        delta: rc - p.capital_weight,
      };
    })
    .sort((a, b) => Math.abs(b.delta) - Math.abs(a.delta));
}
