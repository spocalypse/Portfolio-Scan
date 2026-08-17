import { readFileSync } from "node:fs";
import { join } from "node:path";

import type { AnalyzeResponse } from "./types";

/**
 * Loads the frozen contract fixture from repo root.
 * process.cwd() is web/ when Next runs npm scripts from that package.
 */
export function loadSampleAnalyze(): AnalyzeResponse {
  const fixturePath = join(
    process.cwd(),
    "..",
    "fixtures",
    "metrics.sample.json",
  );
  const raw = readFileSync(fixturePath, "utf8");
  return JSON.parse(raw) as AnalyzeResponse;
}
