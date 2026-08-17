/** Shapes mirrored from api/src/px/schemas/extract.py (ExtractResponse). Do not invent fields. */

export type ExtractRow = {
  raw_label: string;
  ticker_guess: string | null;
  quantity: number | null;
  market_value: number | null;
  confidence: number;
};

export type ExtractResponse = {
  rows: ExtractRow[];
  total_value: number | null;
  brokerage_guess: string | null;
  warnings: string[];
  model_used: string;
};

/** Confirm-UI only — not part of ExtractResponse. Ambiguous rows need an exchange pick. */
export type ExchangeOption = "NYSE" | "NASDAQ" | "AMEX" | "Other";

export type ConfirmRow = {
  id: string;
  raw_label: string;
  ticker: string;
  quantity: number | null;
  market_value: number | null;
  /** Capital weight in [0,1], derived from market_value share of editable total. */
  weight: number;
  confidence: number;
  exchange: ExchangeOption;
};
