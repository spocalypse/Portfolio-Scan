import type { SectorExposure } from "@/lib/types";
import { formatPct } from "@/lib/format";

type SectorDualBarChartProps = {
  rows: SectorExposure[];
};

/**
 * Dual horizontal bars: capital (--capital) above risk (--risk).
 * Value labels sit on the right so color is never the sole channel.
 */
export function SectorDualBarChart({ rows }: SectorDualBarChartProps) {
  const sorted = [...rows].sort(
    (a, b) =>
      Math.abs(b.risk_contribution_pct - b.capital_weight) -
      Math.abs(a.risk_contribution_pct - a.capital_weight),
  );
  const maxVal = Math.max(
    0.01,
    ...sorted.flatMap((r) => [r.capital_weight, r.risk_contribution_pct]),
  );
  const rowH = 44;
  const labelW = 168;
  const barH = 6;
  const width = 720;
  const plotW = width - labelW - 96;
  const height = sorted.length * rowH + 8;

  return (
    <div style={{ width: "100%", overflowX: "auto" }}>
      <svg
        role="img"
        aria-label="Sector capital weight versus risk contribution"
        viewBox={`0 0 ${width} ${height}`}
        width="100%"
        style={{ display: "block", maxWidth: "1040px", height: "auto" }}
      >
        {sorted.map((row, i) => {
          const y = i * rowH + 8;
          const capW = (row.capital_weight / maxVal) * plotW;
          const riskW = (row.risk_contribution_pct / maxVal) * plotW;
          const short =
            row.sector.length > 22 ? `${row.sector.slice(0, 20)}…` : row.sector;
          return (
            <g key={row.sector} transform={`translate(0, ${y})`}>
              <text
                x={0}
                y={barH + 4}
                fill="var(--text)"
                fontSize="12"
                fontFamily="var(--font-body), system-ui, sans-serif"
              >
                {short}
              </text>
              <rect
                x={labelW}
                y={0}
                width={Math.max(1, capW)}
                height={barH}
                fill="var(--capital)"
              />
              <rect
                x={labelW}
                y={barH + 4}
                width={Math.max(1, riskW)}
                height={barH}
                fill="var(--risk)"
              />
              <text
                x={width}
                y={barH + 4}
                textAnchor="end"
                fontSize="12"
                fontFamily="var(--font-numeral), ui-monospace, monospace"
              >
                <tspan fill="var(--capital)">{formatPct(row.capital_weight, 0)}</tspan>
                <tspan fill="var(--muted)"> / </tspan>
                <tspan fill="var(--risk)">{formatPct(row.risk_contribution_pct, 0)}</tspan>
              </text>
              <title>{`${row.sector}: capital ${formatPct(row.capital_weight)}, risk ${formatPct(row.risk_contribution_pct)}`}</title>
            </g>
          );
        })}
      </svg>
    </div>
  );
}
