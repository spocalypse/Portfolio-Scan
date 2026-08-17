"use client";

import {
  useCallback,
  useEffect,
  useId,
  useRef,
  useState,
  type CSSProperties,
  type PointerEvent as ReactPointerEvent,
} from "react";

import {
  normalizeRect,
  prepareScreenshot,
  PrepareError,
  type RedactionRect,
} from "@/lib/image-prepare";

const TOOLBAR: CSSProperties = {
  display: "flex",
  flexWrap: "wrap",
  gap: "8px",
  alignItems: "center",
};

const BTN: CSSProperties = {
  margin: 0,
  padding: "10px 14px",
  border: "1px solid var(--rule)",
  backgroundColor: "var(--panel)",
  color: "var(--text)",
  fontSize: "var(--step-2)",
  letterSpacing: "0.08em",
  textTransform: "uppercase",
  cursor: "pointer",
};

const BTN_PRIMARY: CSSProperties = {
  ...BTN,
  borderColor: "var(--text)",
  backgroundColor: "var(--text)",
  color: "var(--void)",
};

type DragState = {
  pointerId: number;
  originX: number;
  originY: number;
  currentX: number;
  currentY: number;
};

type RedactStageProps = {
  sourceFile: File;
  onPrepared: (prepared: File) => void;
  onBack: () => void;
};

export function RedactStage({ sourceFile, onPrepared, onBack }: RedactStageProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const naturalRef = useRef<{ width: number; height: number } | null>(null);
  const imageRef = useRef<HTMLImageElement | null>(null);
  const [rects, setRects] = useState<RedactionRect[]>([]);
  const [drag, setDrag] = useState<DragState | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [ready, setReady] = useState(false);
  const headingId = useId();

  const paint = useCallback(() => {
    const canvas = canvasRef.current;
    const img = imageRef.current;
    const natural = naturalRef.current;
    if (!canvas || !img || !natural) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const maxDisplay = 720;
    const longEdge = Math.max(natural.width, natural.height);
    const displayScale = longEdge > maxDisplay ? maxDisplay / longEdge : 1;
    const dw = Math.max(1, Math.round(natural.width * displayScale));
    const dh = Math.max(1, Math.round(natural.height * displayScale));
    canvas.width = dw;
    canvas.height = dh;

    // Canvas 2D needs a concrete paint; keyword avoids a hex outside tokens.css.
    ctx.fillStyle = "black";
    ctx.fillRect(0, 0, dw, dh);
    ctx.drawImage(img, 0, 0, dw, dh);

    ctx.fillStyle = "black";
    for (const r of rects) {
      ctx.fillRect(r.x * displayScale, r.y * displayScale, r.w * displayScale, r.h * displayScale);
    }

    if (drag) {
      const preview = normalizeRect(drag.originX, drag.originY, drag.currentX, drag.currentY);
      if (preview) {
        ctx.fillRect(
          preview.x * displayScale,
          preview.y * displayScale,
          preview.w * displayScale,
          preview.h * displayScale,
        );
      }
    }
  }, [drag, rects]);

  useEffect(() => {
    let revoked = false;
    const url = URL.createObjectURL(sourceFile);
    const img = new Image();
    img.onload = () => {
      if (revoked) return;
      imageRef.current = img;
      naturalRef.current = { width: img.naturalWidth, height: img.naturalHeight };
      setReady(true);
    };
    img.onerror = () => {
      if (revoked) return;
      setError("Couldn't read that image — try a full-screen capture of the holdings list.");
    };
    img.src = url;
    return () => {
      revoked = true;
      URL.revokeObjectURL(url);
      imageRef.current = null;
      naturalRef.current = null;
    };
  }, [sourceFile]);

  useEffect(() => {
    if (ready) paint();
  }, [ready, paint]);

  function canvasToNatural(event: ReactPointerEvent<HTMLCanvasElement>): { x: number; y: number } | null {
    const canvas = canvasRef.current;
    const natural = naturalRef.current;
    if (!canvas || !natural) return null;
    const bounds = canvas.getBoundingClientRect();
    if (bounds.width <= 0 || bounds.height <= 0) return null;
    const x = ((event.clientX - bounds.left) / bounds.width) * natural.width;
    const y = ((event.clientY - bounds.top) / bounds.height) * natural.height;
    return {
      x: Math.min(Math.max(0, x), natural.width),
      y: Math.min(Math.max(0, y), natural.height),
    };
  }

  function onPointerDown(event: ReactPointerEvent<HTMLCanvasElement>) {
    if (busy) return;
    const pt = canvasToNatural(event);
    if (!pt) return;
    event.currentTarget.setPointerCapture(event.pointerId);
    setDrag({
      pointerId: event.pointerId,
      originX: pt.x,
      originY: pt.y,
      currentX: pt.x,
      currentY: pt.y,
    });
  }

  function onPointerMove(event: ReactPointerEvent<HTMLCanvasElement>) {
    setDrag((prev) => {
      if (!prev || prev.pointerId !== event.pointerId) return prev;
      const pt = canvasToNatural(event);
      if (!pt) return prev;
      return { ...prev, currentX: pt.x, currentY: pt.y };
    });
  }

  function onPointerUp(event: ReactPointerEvent<HTMLCanvasElement>) {
    setDrag((prev) => {
      if (!prev || prev.pointerId !== event.pointerId) return prev;
      const pt = canvasToNatural(event) ?? { x: prev.currentX, y: prev.currentY };
      const next = normalizeRect(prev.originX, prev.originY, pt.x, pt.y);
      if (next) setRects((list) => [...list, next]);
      return null;
    });
  }

  async function handleContinue() {
    setError(null);
    setBusy(true);
    try {
      const prepared = await prepareScreenshot(sourceFile, rects);
      onPrepared(prepared);
    } catch (err) {
      const message =
        err instanceof PrepareError
          ? err.message
          : "Couldn't prepare that image — try again with a different capture.";
      setError(message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
      <header style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
        <p className="eyebrow">Portfolio X-Ray</p>
        <h1
          id={headingId}
          style={{
            margin: 0,
            fontSize: "var(--step-5)",
            fontWeight: 500,
            letterSpacing: "0.04em",
            lineHeight: 1.1,
          }}
        >
          Redact
        </h1>
        <p style={{ margin: 0, fontSize: "var(--step-3)", color: "var(--muted)", maxWidth: "40em" }}>
          Drag black boxes over anything that should never leave this device. Covered pixels are
          burned out before the image is prepared — EXIF is stripped and the long edge is capped at
          1600px.
        </p>
      </header>

      <div
        style={{
          border: "1px solid var(--rule)",
          backgroundColor: "var(--panel)",
          padding: "12px",
          overflow: "auto",
        }}
      >
        <canvas
          ref={canvasRef}
          role="img"
          aria-labelledby={headingId}
          onPointerDown={onPointerDown}
          onPointerMove={onPointerMove}
          onPointerUp={onPointerUp}
          onPointerCancel={onPointerUp}
          style={{
            display: "block",
            maxWidth: "100%",
            height: "auto",
            cursor: busy ? "wait" : "crosshair",
            touchAction: "none",
          }}
        />
      </div>

      <div style={TOOLBAR}>
        <button type="button" style={BTN} onClick={onBack} disabled={busy}>
          Back
        </button>
        <button
          type="button"
          style={BTN}
          onClick={() => setRects((list) => list.slice(0, -1))}
          disabled={busy || rects.length === 0}
        >
          Undo
        </button>
        <button
          type="button"
          style={BTN}
          onClick={() => setRects([])}
          disabled={busy || rects.length === 0}
        >
          Clear
        </button>
        <span style={{ flex: 1 }} />
        <button type="button" style={BTN_PRIMARY} onClick={handleContinue} disabled={busy || !ready}>
          {busy ? "Preparing…" : "Continue"}
        </button>
      </div>

      {error ? (
        <p style={{ margin: 0, fontSize: "var(--step-2)", color: "var(--alert)" }}>{error}</p>
      ) : (
        <p style={{ margin: 0, fontSize: "var(--step-2)", color: "var(--muted)" }}>
          {rects.length === 0
            ? "No redactions yet — continue if the screenshot is already clean."
            : `${rects.length} redaction${rects.length === 1 ? "" : "s"} will be burned into the prepared image.`}
        </p>
      )}
    </div>
  );
}
