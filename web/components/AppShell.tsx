"use client";

import { useState } from "react";

import { ConfirmHoldingsTable } from "@/components/ConfirmHoldingsTable";
import { InstrumentReadout } from "@/components/InstrumentReadout";
import { RedactStage } from "@/components/RedactStage";
import { UploadDropzone } from "@/components/UploadDropzone";
import { extractToConfirmRows, recomputeWeights } from "@/lib/confirm-rows";
import type { ConfirmRow, ExtractResponse } from "@/lib/extract-types";
import type { AnalyzeResponse } from "@/lib/types";

type Stage = "upload" | "redact" | "confirm" | "readout";

type AppShellProps = {
  analyzeFixture: AnalyzeResponse;
  extractSample: ExtractResponse;
};

export function AppShell({ analyzeFixture, extractSample }: AppShellProps) {
  const [stage, setStage] = useState<Stage>("upload");
  const [sourceFile, setSourceFile] = useState<File | null>(null);
  const [preparedFile, setPreparedFile] = useState<File | null>(null);
  const [rows, setRows] = useState<ConfirmRow[]>([]);
  const [warnings, setWarnings] = useState<string[]>([]);
  const [brokerageGuess, setBrokerageGuess] = useState<string | null>(null);

  function handleFileAccepted(file: File) {
    // Raw pick stays in memory only until prepare replaces it.
    setSourceFile(file);
    setPreparedFile(null);
    setStage("redact");
  }

  function handlePrepared(file: File) {
    // Prepared JPEG (EXIF stripped, downscaled, redactions burned) — never disk / localStorage.
    setPreparedFile(file);
    setSourceFile(null);
    // Mock extract until live /api/extract wiring (#21).
    setRows(extractToConfirmRows(extractSample));
    setWarnings(extractSample.warnings);
    setBrokerageGuess(extractSample.brokerage_guess);
    setStage("confirm");
  }

  function handleRowsChange(next: ConfirmRow[]) {
    setRows(recomputeWeights(next));
  }

  function handleBackToUpload() {
    setSourceFile(null);
    setPreparedFile(null);
    setRows([]);
    setWarnings([]);
    setBrokerageGuess(null);
    setStage("upload");
  }

  function handleAnalyze() {
    // Demo path: confirmed holdings stay client-side as {ticker, weight} only.
    // Readout still uses the metrics fixture until live analyze exists.
    if (!preparedFile || rows.length === 0) return;
    setStage("readout");
  }

  return (
    <main
      style={{
        maxWidth: "1040px",
        margin: "0 auto",
        padding: "48px 16px 64px",
        display: "flex",
        flexDirection: "column",
        gap: "0",
      }}
    >
      {stage === "upload" ? <UploadDropzone onFileAccepted={handleFileAccepted} /> : null}

      {stage === "redact" && sourceFile ? (
        <RedactStage
          sourceFile={sourceFile}
          onPrepared={handlePrepared}
          onBack={handleBackToUpload}
        />
      ) : null}

      {stage === "confirm" ? (
        <ConfirmHoldingsTable
          rows={rows}
          warnings={warnings}
          brokerageGuess={brokerageGuess}
          onChange={handleRowsChange}
          onAnalyze={handleAnalyze}
          onBack={handleBackToUpload}
        />
      ) : null}

      {stage === "readout" ? (
        <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
          <button
            type="button"
            onClick={handleBackToUpload}
            style={{
              alignSelf: "flex-start",
              margin: 0,
              padding: "8px 0",
              border: "none",
              background: "transparent",
              color: "var(--muted)",
              fontSize: "var(--step-1)",
              letterSpacing: "0.12em",
              textTransform: "uppercase",
              cursor: "pointer",
            }}
          >
            Start over
          </button>
          <InstrumentReadout
            data={analyzeFixture}
            fixtureNotice="You confirmed holdings above. Metrics below are still the frozen fixture until live analyze exists."
          />
        </div>
      ) : null}
    </main>
  );
}
