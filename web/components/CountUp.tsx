"use client";

import { useEffect, useState } from "react";

type CountUpProps = {
  value: number;
  /** Format the interpolating number for display (tabular-friendly). */
  format: (n: number) => string;
  durationMs?: number;
};

/**
 * SPEC §5.11: numerals count up once on load, then stop.
 * `prefers-reduced-motion: reduce` → final value immediately.
 */
export function CountUp({ value, format, durationMs = 900 }: CountUpProps) {
  const [text, setText] = useState(() => format(0));

  useEffect(() => {
    let frame = 0;
    let startFrame = 0;

    const start = () => {
      const reduced =
        typeof window !== "undefined" &&
        window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      if (reduced || durationMs <= 0) {
        setText(format(value));
        return;
      }

      const t0 = performance.now();
      const from = 0;
      const to = value;

      const tick = (now: number) => {
        const t = Math.min(1, (now - t0) / durationMs);
        const eased = 1 - (1 - t) ** 3;
        setText(format(from + (to - from) * eased));
        if (t < 1) {
          frame = requestAnimationFrame(tick);
        } else {
          setText(format(to));
        }
      };

      frame = requestAnimationFrame(tick);
    };

    // Defer so setState is not synchronous inside the effect body (eslint react-hooks).
    startFrame = requestAnimationFrame(start);
    return () => {
      cancelAnimationFrame(startFrame);
      cancelAnimationFrame(frame);
    };
  }, [value, format, durationMs]);

  return (
    <span className="numeral" style={{ fontVariantNumeric: "tabular-nums" }}>
      {text}
    </span>
  );
}
