"use client";

import { useId, useRef, useState, type CSSProperties, type DragEvent } from "react";

const ZONE: CSSProperties = {
  border: "1px solid var(--rule)",
  backgroundColor: "var(--panel)",
  padding: "48px 24px",
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  justifyContent: "center",
  gap: "16px",
  textAlign: "center",
  cursor: "pointer",
};

type UploadDropzoneProps = {
  onFileAccepted: (file: File) => void;
};

export function UploadDropzone({ onFileAccepted }: UploadDropzoneProps) {
  const inputId = useId();
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function acceptFile(file: File | undefined) {
    setError(null);
    if (!file) return;
    if (!file.type.startsWith("image/")) {
      setError("Choose an image file (PNG, JPEG, or WebP).");
      return;
    }
    onFileAccepted(file);
  }

  function onDrop(event: DragEvent<HTMLLabelElement>) {
    event.preventDefault();
    setDragging(false);
    acceptFile(event.dataTransfer.files[0]);
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
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
          Upload
        </h1>
        <p style={{ margin: 0, fontSize: "var(--step-3)", color: "var(--muted)", maxWidth: "36em" }}>
          Drop a screenshot of your holdings. The image stays in memory only — never written to
          disk or localStorage. Canvas redaction lands in #10.
        </p>
      </header>

      <label
        htmlFor={inputId}
        onDragEnter={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={(e) => {
          e.preventDefault();
          setDragging(false);
        }}
        onDrop={onDrop}
        style={{
          ...ZONE,
          position: "relative",
          outline: dragging ? "1px solid var(--text)" : "none",
          outlineOffset: "2px",
        }}
      >
        <p style={{ margin: 0, fontSize: "var(--step-3)" }}>Drop a screenshot of your holdings.</p>
        <p style={{ margin: 0, fontSize: "var(--step-2)", color: "var(--muted)" }}>
          or click to choose a file
        </p>
        <input
          ref={inputRef}
          id={inputId}
          type="file"
          accept="image/*"
          style={{ position: "absolute", inset: 0, opacity: 0, cursor: "pointer" }}
          onChange={(e) => acceptFile(e.target.files?.[0])}
        />
      </label>

      {error ? (
        <p style={{ margin: 0, fontSize: "var(--step-2)", color: "var(--alert)" }}>{error}</p>
      ) : null}
    </div>
  );
}
