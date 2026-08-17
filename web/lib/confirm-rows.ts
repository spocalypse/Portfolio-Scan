import type { ConfirmRow, ExchangeOption, ExtractResponse } from "./extract-types";

const DEFAULT_EXCHANGE: ExchangeOption = "NASDAQ";

export function extractToConfirmRows(extract: ExtractResponse): ConfirmRow[] {
  const total = sumMarketValues(extract.rows.map((r) => r.market_value));

  return extract.rows.map((row, index) => {
    const market_value = row.market_value;
    const weight =
      total > 0 && market_value != null && market_value > 0 ? market_value / total : 0;

    return {
      id: `row-${index}`,
      raw_label: row.raw_label,
      ticker: row.ticker_guess ?? "",
      quantity: row.quantity,
      market_value,
      weight,
      confidence: row.confidence,
      exchange: DEFAULT_EXCHANGE,
    };
  });
}

export function recomputeWeights(rows: ConfirmRow[]): ConfirmRow[] {
  const total = sumMarketValues(rows.map((r) => r.market_value));
  if (total <= 0) {
    return rows.map((r) => ({ ...r, weight: 0 }));
  }
  return rows.map((r) => ({
    ...r,
    weight: r.market_value != null && r.market_value > 0 ? r.market_value / total : 0,
  }));
}

function sumMarketValues(values: Array<number | null>): number {
  return values.reduce<number>((acc, v) => (v != null && v > 0 ? acc + v : acc), 0);
}
