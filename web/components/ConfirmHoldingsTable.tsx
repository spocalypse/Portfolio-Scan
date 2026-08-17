"use client";

import type { CSSProperties } from "react";

import { formatPct } from "@/lib/format";
import type { ConfirmRow, ExchangeOption } from "@/lib/extract-types";

const EXCHANGES: ExchangeOption[] = ["NYSE", "NASDAQ", "AMEX", "Other"];

const LABEL: CSSProperties = {
  margin: 0,
  fontSize: "var(--step-1)",
  letterSpacing: "0.12em",
  textTransform: "uppercase",
  color: "var(--muted)",
};

const INPUT: CSSProperties = {
  width: "100%",
  boxSizing: "border-box",
  margin: 0,
  padding: "8px",
  border: "1px solid var(--rule)",
  backgroundColor: "var(--panel)",
  color: "var(--text)",
  fontFamily: "var(--font-numeral), ui-monospace, monospace",
  fontVariantNumeric: "tabular-nums",
  fontSize: "var(--step-2)",
  outline: "none",
};

const BTN: CSSProperties = {
  margin: 0,
  padding: "12px 16px",
  border: "1px solid var(--rule)",
  backgroundColor: "var(--panel)",
  color: "var(--text)",
  fontSize: "var(--step-2)",
  letterSpacing: "0.08em",
  textTransform: "uppercase",
  cursor: "pointer",
};

type ConfirmHoldingsTableProps = {
  rows: ConfirmRow[];
  warnings: string[];
  brokerageGuess: string | null;
  onChange: (rows: ConfirmRow[]) => void;
  onAnalyze: () => void;
  onBack: () => void;
};

export function ConfirmHoldingsTable({
  rows,
  warnings,
  brokerageGuess,
  onChange,
  onAnalyze,
  onBack,
}: ConfirmHoldingsTableProps) {
  const canAnalyze = rows.length > 0 && rows.every((r) => r.ticker.trim().length > 0);

  function updateRow(id: string, patch: Partial<ConfirmRow>) {
    onChange(rows.map((r) => (r.id === id ? { ...r, ...patch } : r)));
  }

  function removeRow(id: string) {
    onChange(rows.filter((r) => r.id !== id));
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      <header style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
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
          Confirm holdings
        </h1>
        <p style={{ margin: 0, fontSize: "var(--step-3)", color: "var(--muted)", maxWidth: "36em" }}>
          Correct every row before analysis. Weights are capital shares of market value — not
          balances sent downstream.
          {brokerageGuess ? ` Brokerage guess: ${brokerageGuess}.` : null}
        </p>
      </header>

      {warnings.length > 0 ? (
        <section
          aria-label="Extraction warnings"
          style={{
            borderTop: "1px solid var(--rule)",
            paddingTop: "16px",
            display: "flex",
            flexDirection: "column",
            gap: "8px",
          }}
        >
          <p className="eyebrow" style={{ color: "var(--alert)" }}>
            Notices
          </p>
          {warnings.map((w) => (
            <p key={w} style={{ margin: 0, fontSize: "var(--step-2)", color: "var(--muted)" }}>
              {w}
            </p>
          ))}
        </section>
      ) : null}

      <div style={{ overflowX: "auto" }}>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1.2fr 88px 72px 88px 72px 96px 64px",
            gap: "8px",
            minWidth: "720px",
            paddingBottom: "8px",
          }}
        >
          <p style={LABEL}>Label / ticker</p>
          <p style={{ ...LABEL, textAlign: "right" }}>Qty</p>
          <p style={{ ...LABEL, textAlign: "right" }}>Value</p>
          <p style={{ ...LABEL, textAlign: "right" }}>Weight</p>
          <p style={{ ...LABEL, textAlign: "right" }}>Conf</p>
          <p style={LABEL}>Exchange</p>
          <p style={LABEL}> </p>
        </div>

        {rows.map((row) => {
          const ambiguous = row.confidence === 0;
          return (
            <div
              key={row.id}
              style={{
                display: "grid",
                gridTemplateColumns: "1.2fr 88px 72px 88px 72px 96px 64px",
                gap: "8px",
                minWidth: "720px",
                borderTop: "1px solid var(--rule)",
                paddingTop: "8px",
                paddingBottom: "8px",
                alignItems: "center",
              }}
            >
              <div style={{ display: "flex", flexDirection: "column", gap: "4px", minWidth: 0 }}>
                <span style={{ fontSize: "var(--step-1)", color: "var(--muted)" }}>{row.raw_label}</span>
                <input
                  aria-label={`Ticker for ${row.raw_label}`}
                  value={row.ticker}
                  onChange={(e) => updateRow(row.id, { ticker: e.target.value.toUpperCase() })}
                  style={{
                    ...INPUT,
                    borderColor: ambiguous || !row.ticker.trim() ? "var(--alert)" : "var(--rule)",
                  }}
                  onFocus={(e) => {
                    e.currentTarget.style.outline = "1px solid var(--text)";
                    e.currentTarget.style.outlineOffset = "2px";
                  }}
                  onBlur={(e) => {
                    e.currentTarget.style.outline = "none";
                  }}
                />
              </div>

              <input
                aria-label={`Quantity for ${row.raw_label}`}
                className="numeral"
                type="text"
                inputMode="decimal"
                value={row.quantity == null ? "" : String(row.quantity)}
                onChange={(e) => {
                  const v = parseOptionalNumber(e.target.value);
                  updateRow(row.id, { quantity: v });
                }}
                style={{ ...INPUT, textAlign: "right" }}
                onFocus={(e) => {
                  e.currentTarget.style.outline = "1px solid var(--text)";
                  e.currentTarget.style.outlineOffset = "2px";
                }}
                onBlur={(e) => {
                  e.currentTarget.style.outline = "none";
                }}
              />

              <input
                aria-label={`Market value for ${row.raw_label}`}
                className="numeral"
                type="text"
                inputMode="decimal"
                value={row.market_value == null ? "" : String(row.market_value)}
                onChange={(e) => {
                  const v = parseOptionalNumber(e.target.value);
                  updateRow(row.id, { market_value: v });
                }}
                style={{ ...INPUT, textAlign: "right" }}
                onFocus={(e) => {
                  e.currentTarget.style.outline = "1px solid var(--text)";
                  e.currentTarget.style.outlineOffset = "2px";
                }}
                onBlur={(e) => {
                  e.currentTarget.style.outline = "none";
                }}
              />

              <span className="numeral" style={{ fontSize: "var(--step-2)", textAlign: "right" }}>
                {formatPct(row.weight)}
              </span>

              <span
                className="numeral"
                style={{
                  fontSize: "var(--step-2)",
                  textAlign: "right",
                  color: ambiguous ? "var(--alert)" : "var(--text)",
                }}
              >
                {row.confidence.toFixed(2)}
              </span>

              <select
                aria-label={`Exchange for ${row.raw_label}`}
                value={row.exchange}
                onChange={(e) => updateRow(row.id, { exchange: e.target.value as ExchangeOption })}
                style={{
                  ...INPUT,
                  borderColor: ambiguous ? "var(--alert)" : "var(--rule)",
                }}
                onFocus={(e) => {
                  e.currentTarget.style.outline = "1px solid var(--text)";
                  e.currentTarget.style.outlineOffset = "2px";
                }}
                onBlur={(e) => {
                  e.currentTarget.style.outline = "none";
                }}
              >
                {EXCHANGES.map((ex) => (
                  <option key={ex} value={ex}>
                    {ex}
                  </option>
                ))}
              </select>

              <button
                type="button"
                onClick={() => removeRow(row.id)}
                style={{
                  ...BTN,
                  padding: "8px",
                  fontSize: "var(--step-1)",
                  color: "var(--muted)",
                }}
              >
                Remove
              </button>
            </div>
          );
        })}
      </div>

      {rows.length === 0 ? (
        <p style={{ margin: 0, fontSize: "var(--step-2)", color: "var(--alert)" }}>
          All rows removed. Go back and upload again, or keep at least one holding.
        </p>
      ) : null}

      <div style={{ display: "flex", gap: "8px", flexWrap: "wrap", paddingTop: "8px" }}>
        <button type="button" onClick={onBack} style={BTN}>
          Back
        </button>
        <button
          type="button"
          onClick={onAnalyze}
          disabled={!canAnalyze}
          style={{
            ...BTN,
            borderColor: canAnalyze ? "var(--text)" : "var(--rule)",
            color: canAnalyze ? "var(--text)" : "var(--muted)",
            cursor: canAnalyze ? "pointer" : "not-allowed",
          }}
        >
          Analyze
        </button>
      </div>
    </div>
  );
}

function parseOptionalNumber(raw: string): number | null {
  const trimmed = raw.trim();
  if (trimmed === "") return null;
  const n = Number(trimmed);
  return Number.isFinite(n) ? n : null;
}
