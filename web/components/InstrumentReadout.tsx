"use client";

import { useCallback, type CSSProperties, type ReactNode } from "react";

import { CountUp } from "@/components/CountUp";
import { DivergenceBar } from "@/components/DivergenceBar";
import { buildHoldingsRows } from "@/lib/holdings";
import { HoldingsTable } from "@/components/HoldingsTable";
import { SectorDualBarChart } from "@/components/SectorDualBarChart";
import { formatNum, formatPct, formatTimestamp } from "@/lib/format";
import type { AnalyzeResponse } from "@/lib/types";

const PANEL: CSSProperties = {
  borderTop: "1px solid var(--rule)",
  paddingTop: "24px",
  paddingBottom: "24px",
  display: "flex",
  flexDirection: "column",
  gap: "16px",
};

const LABEL: CSSProperties = {
  margin: 0,
  fontSize: "var(--step-1)",
  letterSpacing: "0.12em",
  textTransform: "uppercase",
  color: "var(--muted)",
};

type InstrumentReadoutProps = {
  data: AnalyzeResponse;
  /** Honest demo copy when metrics are still fixture-backed. */
  fixtureNotice?: string;
};

export function InstrumentReadout({
  data,
  fixtureNotice = "Metrics below are still the frozen fixture until live analyze is wired.",
}: InstrumentReadoutProps) {
  const { metrics, findings, meta } = data;
  const m1 = metrics.m1_weights;
  const m2 = metrics.m2_beta;
  const m3 = metrics.m3_risk_contribution;
  const m4 = metrics.m4_effective_bets;
  const m5 = metrics.m5_factor_tilts;
  const m6 = metrics.m6_etf_look_through;

  const primaryFinding = findings[0] ?? null;
  const holdingsRows = buildHoldingsRows(m1.position_weights, m3.contributions);
  const topDivergence = [...m1.sector_exposure].sort(
    (a, b) =>
      Math.abs(b.risk_contribution_pct - b.capital_weight) -
      Math.abs(a.risk_contribution_pct - a.capital_weight),
  )[0];

  const fmtNum1 = useCallback((n: number) => formatNum(n, 1), []);
  const fmtNum2 = useCallback((n: number) => formatNum(n, 2), []);
  const fmtPct0 = useCallback((n: number) => formatPct(n, 0), []);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "0" }}>
      <header style={{ display: "flex", flexDirection: "column", gap: "8px", paddingBottom: "24px" }}>
        <p className="eyebrow">Portfolio X-Ray</p>
        <h1
          style={{
            margin: 0,
            fontSize: "var(--step-5)",
            fontWeight: 500,
            letterSpacing: "0.04em",
            lineHeight: 1.1,
          }}
        >
          Instrument readout
        </h1>
        <p style={{ margin: 0, fontSize: "var(--step-3)", color: "var(--muted)", maxWidth: "40em" }}>
          {fixtureNotice}
        </p>
      </header>

      {primaryFinding ? (
        <section style={{ ...PANEL, paddingTop: "16px" }} aria-label="Primary finding">
          <p className="eyebrow" style={{ color: "var(--text)" }}>
            {primaryFinding.severity} · primary
          </p>
          <h2
            style={{
              margin: 0,
              fontSize: "var(--step-4)",
              fontWeight: 500,
              lineHeight: 1.25,
              maxWidth: "28em",
            }}
          >
            {primaryFinding.headline}
          </h2>
          <p style={{ margin: 0, fontSize: "var(--step-2)", color: "var(--muted)", lineHeight: 1.5, maxWidth: "42em" }}>
            {primaryFinding.explanation}
          </p>
        </section>
      ) : null}

      <section style={PANEL} aria-label="Headline instruments">
        <p className="eyebrow">Headline</p>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))",
            gap: "24px 16px",
          }}
        >
          <MetricCell
            label="Effective bets"
            hint={`vs ${m4.naive_position_count} positions`}
            hero
          >
            <CountUp value={m4.effective_number_of_bets} format={fmtNum1} />
          </MetricCell>
          <MetricCell label="Portfolio beta" hint={`R² ${formatPct(m2.r_squared, 0)}`} hero>
            <CountUp value={m2.beta} format={fmtNum2} />
          </MetricCell>
          <MetricCell label="Portfolio vol" hint="annualized" hero>
            <CountUp value={m3.portfolio_volatility} format={fmtPct0} />
          </MetricCell>
          <MetricCell label="HHI / eff. positions" hint={`${formatNum(m1.effective_position_count, 1)} by weight`}>
            <span className="numeral">{formatNum(m1.hhi, 3)}</span>
          </MetricCell>
        </div>
      </section>

      <section style={PANEL} aria-label="Sector capital versus risk">
        <p className="eyebrow">Sector capital vs risk</p>
        <p style={{ margin: 0, fontSize: "var(--step-2)", color: "var(--muted)", maxWidth: "42em" }}>
          <span style={{ color: "var(--capital)" }}>Capital</span> is what you own.{" "}
          <span style={{ color: "var(--risk)" }}>Risk</span> is contribution to portfolio
          volatility. The amber band is divergence — the product&apos;s signature glyph.
        </p>
        <div
          style={{
            display: "flex",
            gap: "24px",
            flexWrap: "wrap",
            fontSize: "var(--step-1)",
            letterSpacing: "0.12em",
            textTransform: "uppercase",
            color: "var(--muted)",
          }}
        >
          <span>
            <span style={{ color: "var(--capital)" }}>■</span> Capital weight
          </span>
          <span>
            <span style={{ color: "var(--risk)" }}>■</span> Risk contribution
          </span>
        </div>

        {topDivergence ? (
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: "12px",
              borderTop: "1px solid var(--rule)",
              paddingTop: "16px",
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                gap: "16px",
                flexWrap: "wrap",
                alignItems: "baseline",
              }}
            >
              <span style={{ fontSize: "var(--step-3)" }}>
                Largest divergence · {topDivergence.sector}
              </span>
              <span className="numeral" style={{ fontSize: "var(--step-3)", color: "var(--muted)" }}>
                <span style={{ color: "var(--capital)" }}>{formatPct(topDivergence.capital_weight)}</span>
                {" / "}
                <span style={{ color: "var(--risk)" }}>
                  {formatPct(topDivergence.risk_contribution_pct)}
                </span>
                {" · Δ "}
                {formatPct(topDivergence.risk_contribution_pct - topDivergence.capital_weight)}
              </span>
            </div>
            <DivergenceBar
              capitalWeight={topDivergence.capital_weight}
              riskContributionPct={topDivergence.risk_contribution_pct}
              size="lg"
            />
          </div>
        ) : null}

        <SectorDualBarChart rows={m1.sector_exposure} />

        <div style={{ display: "flex", flexDirection: "column", gap: "0" }}>
          {m1.sector_exposure.map((row) => (
            <div
              key={row.sector}
              style={{
                borderTop: "1px solid var(--rule)",
                paddingTop: "12px",
                paddingBottom: "12px",
                display: "flex",
                flexDirection: "column",
                gap: "8px",
              }}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  gap: "16px",
                  flexWrap: "wrap",
                  alignItems: "baseline",
                }}
              >
                <span style={{ fontSize: "var(--step-2)" }}>{row.sector}</span>
                <span className="numeral" style={{ fontSize: "var(--step-2)", color: "var(--muted)" }}>
                  <span style={{ color: "var(--capital)" }}>{formatPct(row.capital_weight)}</span>
                  {" / "}
                  <span style={{ color: "var(--risk)" }}>{formatPct(row.risk_contribution_pct)}</span>
                </span>
              </div>
              <DivergenceBar
                capitalWeight={row.capital_weight}
                riskContributionPct={row.risk_contribution_pct}
              />
            </div>
          ))}
        </div>
      </section>

      <section style={PANEL} aria-label="Holdings">
        <p className="eyebrow">Holdings</p>
        <HoldingsTable rows={holdingsRows} />
      </section>

      <section style={PANEL} aria-label="Findings">
        <p className="eyebrow">All findings</p>
        <ul style={{ listStyle: "none", margin: 0, padding: 0, display: "flex", flexDirection: "column", gap: "0" }}>
          {findings.map((finding) => (
            <li
              key={finding.headline}
              style={{
                borderTop: "1px solid var(--rule)",
                paddingTop: "16px",
                paddingBottom: "16px",
                display: "flex",
                flexDirection: "column",
                gap: "8px",
              }}
            >
              <div style={{ display: "flex", gap: "12px", alignItems: "baseline", flexWrap: "wrap" }}>
                <span className="eyebrow" style={{ color: "var(--text)" }}>
                  {finding.severity}
                </span>
                <h2 style={{ margin: 0, fontSize: "var(--step-3)", fontWeight: 500, lineHeight: 1.35 }}>
                  {finding.headline}
                </h2>
              </div>
              <p style={{ margin: 0, fontSize: "var(--step-2)", color: "var(--muted)", lineHeight: 1.5 }}>
                {finding.explanation}
              </p>
              <p style={{ margin: 0, fontSize: "var(--step-1)", color: "var(--muted)", letterSpacing: "0.04em" }}>
                refs · {finding.metrics_referenced.join(" · ")}
              </p>
            </li>
          ))}
        </ul>
      </section>

      <section style={PANEL} aria-label="Top sector concentration">
        <p className="eyebrow">Top sector concentration</p>
        {m1.top_sector_concentration.map((row) => (
          <div
            key={row.sector}
            style={{
              display: "grid",
              gridTemplateColumns: "minmax(0, 1.4fr) 88px",
              gap: "8px 16px",
              alignItems: "baseline",
              borderTop: "1px solid var(--rule)",
              paddingTop: "8px",
              paddingBottom: "8px",
            }}
          >
            <span style={{ fontSize: "var(--step-2)" }}>{row.sector}</span>
            <span className="numeral" style={{ fontSize: "var(--step-4)", textAlign: "right" }}>
              {formatPct(row.capital_weight)}
            </span>
          </div>
        ))}
      </section>

      <section style={PANEL} aria-label="Risk contribution">
        <p className="eyebrow">Risk contribution</p>
        <p style={{ margin: 0, fontSize: "var(--step-2)", color: "var(--muted)" }}>
          Portfolio volatility {formatPct(m3.portfolio_volatility, 0)}. RC% sums to 100%.
        </p>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "64px repeat(4, 1fr)",
            gap: "8px",
            paddingBottom: "8px",
          }}
        >
          <p style={LABEL}>Ticker</p>
          <p style={{ ...LABEL, textAlign: "right" }}>Weight</p>
          <p style={{ ...LABEL, textAlign: "right" }}>MCR</p>
          <p style={{ ...LABEL, textAlign: "right" }}>RC</p>
          <p style={{ ...LABEL, textAlign: "right" }}>RC%</p>
        </div>
        {m3.contributions.map((row) => (
          <div
            key={row.ticker}
            style={{
              display: "grid",
              gridTemplateColumns: "64px repeat(4, 1fr)",
              gap: "8px",
              borderTop: "1px solid var(--rule)",
              paddingTop: "8px",
              paddingBottom: "8px",
              alignItems: "baseline",
            }}
          >
            <span className="numeral" style={{ fontSize: "var(--step-2)" }}>
              {row.ticker}
            </span>
            <span className="numeral" style={{ fontSize: "var(--step-2)", textAlign: "right" }}>
              {formatPct(row.weight)}
            </span>
            <span className="numeral" style={{ fontSize: "var(--step-2)", textAlign: "right" }}>
              {formatNum(row.mcr, 3)}
            </span>
            <span className="numeral" style={{ fontSize: "var(--step-2)", textAlign: "right" }}>
              {formatNum(row.rc, 4)}
            </span>
            <span className="numeral" style={{ fontSize: "var(--step-2)", textAlign: "right", color: "var(--risk)" }}>
              {formatPct(row.rc_pct)}
            </span>
          </div>
        ))}
      </section>

      <section style={PANEL} aria-label="Factor tilts">
        <p className="eyebrow">Factor tilts</p>
        <p style={{ margin: 0, fontSize: "var(--step-2)", color: "var(--muted)" }}>
          Model R² {formatPct(m5.r_squared, 0)}. Significant when |t| ≥ 2 (flag from fixture).
        </p>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "80px repeat(3, 1fr)",
            gap: "8px",
            paddingBottom: "8px",
          }}
        >
          <p style={LABEL}>Factor</p>
          <p style={{ ...LABEL, textAlign: "right" }}>Loading</p>
          <p style={{ ...LABEL, textAlign: "right" }}>t-stat</p>
          <p style={{ ...LABEL, textAlign: "right" }}>Sig</p>
        </div>
        {m5.loadings.map((row) => (
          <div
            key={row.factor}
            style={{
              display: "grid",
              gridTemplateColumns: "80px repeat(3, 1fr)",
              gap: "8px",
              borderTop: "1px solid var(--rule)",
              paddingTop: "8px",
              paddingBottom: "8px",
              alignItems: "baseline",
            }}
          >
            <span className="numeral" style={{ fontSize: "var(--step-2)" }}>
              {row.factor}
            </span>
            <span className="numeral" style={{ fontSize: "var(--step-2)", textAlign: "right" }}>
              {formatNum(row.loading, 2)}
            </span>
            <span className="numeral" style={{ fontSize: "var(--step-2)", textAlign: "right" }}>
              {formatNum(row.t_stat, 1)}
            </span>
            <span
              className="numeral"
              style={{
                fontSize: "var(--step-2)",
                textAlign: "right",
                color: row.significant ? "var(--text)" : "var(--muted)",
              }}
            >
              {row.significant ? "yes" : "no"}
            </span>
          </div>
        ))}
      </section>

      <section style={PANEL} aria-label="ETF look-through">
        <p className="eyebrow">ETF look-through</p>
        <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
          <MetaLine label="Snapshot date" value={m6.snapshot_date} />
          <MetaLine label="ETFs detected" value={m6.etfs_detected.join(", ")} />
        </div>
        <p className="eyebrow" style={{ marginTop: "8px" }}>
          Pairwise overlap
        </p>
        {m6.pairwise_overlap.map((pair) => (
          <div
            key={`${pair.etf_a}-${pair.etf_b}`}
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 88px",
              gap: "8px",
              borderTop: "1px solid var(--rule)",
              paddingTop: "8px",
              paddingBottom: "8px",
              alignItems: "baseline",
            }}
          >
            <span className="numeral" style={{ fontSize: "var(--step-2)" }}>
              {pair.etf_a} × {pair.etf_b}
            </span>
            <span className="numeral" style={{ fontSize: "var(--step-3)", textAlign: "right" }}>
              {formatPct(pair.overlap_pct)}
            </span>
          </div>
        ))}
        <p className="eyebrow" style={{ marginTop: "8px" }}>
          Look-through weights
        </p>
        {m6.look_through_weights.map((row) => (
          <div
            key={row.ticker}
            style={{
              display: "grid",
              gridTemplateColumns: "88px 1fr",
              gap: "8px",
              borderTop: "1px solid var(--rule)",
              paddingTop: "8px",
              paddingBottom: "8px",
              alignItems: "baseline",
            }}
          >
            <span className="numeral" style={{ fontSize: "var(--step-2)" }}>
              {row.ticker}
            </span>
            <span className="numeral" style={{ fontSize: "var(--step-3)", textAlign: "right" }}>
              {formatPct(row.true_weight, 2)}
            </span>
          </div>
        ))}
      </section>

      <section style={PANEL} aria-label="Excluded holdings">
        <p className="eyebrow">Excluded holdings</p>
        {metrics.excluded_holdings.length === 0 ? (
          <p style={{ margin: 0, fontSize: "var(--step-2)", color: "var(--muted)" }}>None</p>
        ) : (
          metrics.excluded_holdings.map((row) => (
            <div
              key={row.ticker}
              style={{
                borderTop: "1px solid var(--rule)",
                paddingTop: "16px",
                paddingBottom: "8px",
                display: "flex",
                flexDirection: "column",
                gap: "8px",
              }}
            >
              <div style={{ display: "flex", gap: "12px", alignItems: "baseline", flexWrap: "wrap" }}>
                <span className="numeral" style={{ fontSize: "var(--step-4)", color: "var(--alert)" }}>
                  {row.ticker}
                </span>
                <span className="eyebrow" style={{ color: "var(--alert)" }}>
                  {row.reason}
                </span>
              </div>
              <p style={{ margin: 0, fontSize: "var(--step-2)", color: "var(--muted)" }}>{row.detail}</p>
            </div>
          ))
        )}
      </section>

      <section style={PANEL} aria-label="Run metadata">
        <p className="eyebrow">Meta</p>
        <MetaLine label="Request id" value={meta.request_id} />
        <MetaLine label="Computed at" value={formatTimestamp(meta.computed_at)} />
        <MetaLine label="Data window" value={`${meta.data_window_days} days`} />
        <MetaLine label="Price data as of" value={meta.price_data_as_of} />
        <MetaLine
          label="Price data stale"
          value={meta.price_data_stale ? "yes" : "no"}
          alert={meta.price_data_stale}
        />
        <MetaLine label="Narrative model" value={meta.narrative_model_used} />
        <MetaLine
          label="Warnings"
          value={meta.warnings.length === 0 ? "none" : meta.warnings.join("; ")}
        />
      </section>

      <footer
        style={{
          borderTop: "1px solid var(--rule)",
          paddingTop: "24px",
          marginTop: "8px",
        }}
      >
        <p style={{ margin: 0, fontSize: "var(--step-1)", color: "var(--muted)", lineHeight: 1.5 }}>
          Educational analysis of historical data, not investment advice.
        </p>
      </footer>
    </div>
  );
}

function MetricCell({
  label,
  hint,
  hero = false,
  children,
}: {
  label: string;
  hint?: string;
  hero?: boolean;
  children: ReactNode;
}) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
      <p style={LABEL}>{label}</p>
      <p
        className="numeral"
        style={{
          margin: 0,
          fontSize: hero ? "var(--step-5)" : "var(--step-4)",
          lineHeight: 1,
        }}
      >
        {children}
      </p>
      {hint ? (
        <p style={{ margin: 0, fontSize: "var(--step-1)", color: "var(--muted)" }}>{hint}</p>
      ) : null}
    </div>
  );
}

function MetaLine({
  label,
  value,
  alert = false,
}: {
  label: string;
  value: string;
  alert?: boolean;
}) {
  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "160px 1fr",
        gap: "8px 16px",
        borderTop: "1px solid var(--rule)",
        paddingTop: "8px",
        paddingBottom: "8px",
        alignItems: "baseline",
      }}
    >
      <p style={LABEL}>{label}</p>
      <p
        className="numeral"
        style={{
          margin: 0,
          fontSize: "var(--step-2)",
          color: alert ? "var(--alert)" : "var(--text)",
          wordBreak: "break-word",
        }}
      >
        {value}
      </p>
    </div>
  );
}
