type DivergenceBarProps = {
  capitalWeight: number;
  riskContributionPct: number;
  /** Default compact; `lg` for the signature sector instrument. */
  size?: "sm" | "lg";
};

/**
 * SPEC §5.11 signature: capital (blue) above, risk (amber) below,
 * delta zone filled when they diverge.
 */
export function DivergenceBar({
  capitalWeight,
  riskContributionPct,
  size = "sm",
}: DivergenceBarProps) {
  const capitalPct = Math.max(0, Math.min(100, capitalWeight * 100));
  const riskPct = Math.max(0, Math.min(100, riskContributionPct * 100));
  const lo = Math.min(capitalPct, riskPct);
  const hi = Math.max(capitalPct, riskPct);
  const delta = hi - lo;
  const line = size === "lg" ? 3 : 2;
  const band = size === "lg" ? 10 : 6;

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        gap: size === "lg" ? "6px" : "4px",
        width: "100%",
      }}
      aria-hidden="true"
    >
      <div
        style={{
          height: `${line}px`,
          width: `${capitalPct}%`,
          backgroundColor: "var(--capital)",
        }}
      />
      <div
        style={{
          position: "relative",
          height: `${band}px`,
          width: "100%",
          backgroundColor: "var(--panel)",
          borderTop: "1px solid var(--rule)",
          borderBottom: "1px solid var(--rule)",
        }}
      >
        {delta > 0.05 ? (
          <div
            style={{
              position: "absolute",
              left: `${lo}%`,
              width: `${delta}%`,
              top: 0,
              bottom: 0,
              backgroundColor: "var(--risk)",
              opacity: 0.4,
            }}
          />
        ) : null}
      </div>
      <div
        style={{
          height: `${line}px`,
          width: `${riskPct}%`,
          backgroundColor: "var(--risk)",
        }}
      />
    </div>
  );
}
