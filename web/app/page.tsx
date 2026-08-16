const TYPE_STEPS = [
  { step: 1, label: "Step 1 · eyebrow", sample: "SECTOR CONCENTRATION" },
  { step: 2, label: "Step 2 · caption", sample: "Holdings confirmed" },
  { step: 3, label: "Step 3 · body", sample: "Drop a screenshot of your holdings." },
  { step: 4, label: "Step 4 · value", sample: "0.842" },
  { step: 5, label: "Step 5 · hero", sample: "1.240" },
] as const;

export default function Home() {
  return (
    <main
      style={{
        maxWidth: "880px",
        margin: "0 auto",
        padding: "48px 16px",
        display: "flex",
        flexDirection: "column",
        gap: "32px",
      }}
    >
      <header style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
        <p className="eyebrow">Portfolio X-Ray</p>
        <p style={{ margin: 0, fontSize: "var(--step-3)", color: "var(--muted)" }}>
          Drop a screenshot of your holdings.
        </p>
      </header>

      <section
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "24px",
          borderTop: "1px solid var(--rule)",
          paddingTop: "24px",
        }}
        aria-label="Type scale"
      >
        <p className="eyebrow">Type scale</p>
        {TYPE_STEPS.map(({ step, label, sample }) => {
          const isNumeral = step >= 4;
          return (
            <div
              key={step}
              style={{
                display: "flex",
                flexDirection: "column",
                gap: "8px",
                borderTop: "1px solid var(--rule)",
                paddingTop: "16px",
              }}
            >
              <p className="eyebrow">{label}</p>
              <p
                className={isNumeral ? "numeral" : undefined}
                style={{
                  margin: 0,
                  fontSize: `var(--step-${step})`,
                  lineHeight: 1.25,
                }}
              >
                {sample}
              </p>
            </div>
          );
        })}
      </section>
    </main>
  );
}
