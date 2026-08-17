/** Format a [0,1] weight/fraction as a percent string with tabular-friendly decimals. */
export function formatPct(fraction: number, digits = 1): string {
  return `${(fraction * 100).toFixed(digits)}%`;
}

/** Format a unitless number (beta, HHI, loadings, t-stats). */
export function formatNum(value: number, digits = 2): string {
  return value.toFixed(digits);
}

/** Format ISO timestamps for the meta strip (plain string, no locale money styles). */
export function formatTimestamp(iso: string): string {
  return iso.replace("T", " ").replace("Z", " UTC");
}
