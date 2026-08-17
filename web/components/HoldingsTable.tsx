import type { CSSProperties } from "react";

import { formatPct } from "@/lib/format";
import type { HoldingsRow } from "@/lib/holdings";

type HoldingsTableProps = {
  rows: HoldingsRow[];
};

const TH: CSSProperties = {
  margin: 0,
  fontSize: "var(--step-1)",
  letterSpacing: "0.12em",
  textTransform: "uppercase",
  color: "var(--muted)",
  textAlign: "right",
  fontWeight: 500,
  padding: "8px 0",
  borderBottom: "1px solid var(--rule)",
};

const TD: CSSProperties = {
  padding: "10px 0",
  borderBottom: "1px solid var(--rule)",
  fontSize: "var(--step-2)",
  verticalAlign: "baseline",
};

/**
 * Instrument holdings table: capital vs risk with Δ, sorted by |Δ|.
 */
export function HoldingsTable({ rows }: HoldingsTableProps) {
  return (
    <div style={{ width: "100%", overflowX: "auto" }}>
      <table
        style={{
          width: "100%",
          borderCollapse: "collapse",
          minWidth: "520px",
        }}
      >
        <caption
          style={{
            captionSide: "top",
            textAlign: "left",
            paddingBottom: "12px",
            fontSize: "var(--step-2)",
            color: "var(--muted)",
          }}
        >
          Sorted by absolute divergence (risk contribution minus capital weight).
        </caption>
        <thead>
          <tr>
            <th scope="col" style={{ ...TH, textAlign: "left" }}>
              Ticker
            </th>
            <th scope="col" style={{ ...TH, textAlign: "left" }}>
              Sector
            </th>
            <th scope="col" style={TH}>
              Capital
            </th>
            <th scope="col" style={TH}>
              Risk
            </th>
            <th scope="col" style={TH}>
              Δ
            </th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.ticker}>
              <th
                scope="row"
                className="numeral"
                style={{ ...TD, textAlign: "left", fontWeight: 500, fontSize: "var(--step-3)" }}
              >
                {row.ticker}
              </th>
              <td style={{ ...TD, color: "var(--muted)" }}>{row.sector}</td>
              <td className="numeral" style={{ ...TD, textAlign: "right", color: "var(--capital)" }}>
                {formatPct(row.capital_weight)}
              </td>
              <td className="numeral" style={{ ...TD, textAlign: "right", color: "var(--risk)" }}>
                {formatPct(row.risk_contribution_pct)}
              </td>
              <td
                className="numeral"
                style={{
                  ...TD,
                  textAlign: "right",
                  color: Math.abs(row.delta) < 0.005 ? "var(--muted)" : "var(--text)",
                }}
              >
                {row.delta >= 0 ? "+" : ""}
                {formatPct(row.delta)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
