import assert from "node:assert/strict";
import test from "node:test";

import { buildHoldingsRows } from "./holdings.ts";

test("buildHoldingsRows joins capital and risk and sorts by absolute delta", () => {
  const rows = buildHoldingsRows(
    [
      { ticker: "AAPL", sector: "Information Technology", capital_weight: 0.2 },
      { ticker: "JPM", sector: "Financials", capital_weight: 0.1 },
    ],
    [
      { ticker: "AAPL", weight: 0.2, mcr: 1, rc: 0.1, rc_pct: 0.35 },
      { ticker: "JPM", weight: 0.1, mcr: 1, rc: 0.05, rc_pct: 0.08 },
    ],
  );
  assert.equal(rows[0].ticker, "AAPL");
  assert.ok(Math.abs(rows[0].delta - 0.15) < 1e-9);
  assert.equal(rows[1].ticker, "JPM");
});
