type DivergenceBarProps = {
  capitalWeight: number;
  riskContributionPct: number;
};

/**
 * SPEC §5.11 signature: capital (blue) above, risk (amber) below,
 * delta zone filled when they diverge.
 */
export function DivergenceBar({
  capitalWeight,
  riskContributionPct,
}: DivergenceBarProps) {
  const capitalPct = Math.max(0, Math.min(100, capitalWeight * 100));
  const riskPct = Math.max(0, Math.min(100, riskContributionPct * 100));
  const lo = Math.min(capitalPct, riskPct);
  const hi = Math.max(capitalPct, riskPct);
  const delta = hi - lo;

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        gap: "4px",
        width: "100%",
      }}
      aria-hidden="true"
    >
      <div
        style={{
          height: "2px",
          width: `${capitalPct}%`,
          backgroundColor: "var(--capital)",
        }}
      />
      <div
        style={{
          position: "relative",
          height: "6px",
          width: "100%",
          backgroundColor: "var(--panel)",
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
              opacity: 0.35,
            }}
          />
        ) : null}
      </div>
      <div
        style={{
          height: "2px",
          width: `${riskPct}%`,
          backgroundColor: "var(--risk)",
        }}
      />
    </div>
  );
}
