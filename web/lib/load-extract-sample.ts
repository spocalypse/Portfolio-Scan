import { readFileSync } from "node:fs";
import { join } from "node:path";

import type { ExtractResponse } from "./extract-types";

/**
 * Loads the mock extract fixture from repo root.
 * Used until POST /api/extract is wired (#4).
 */
export function loadSampleExtract(): ExtractResponse {
  const fixturePath = join(process.cwd(), "..", "fixtures", "extract.sample.json");
  const raw = readFileSync(fixturePath, "utf8");
  return JSON.parse(raw) as ExtractResponse;
}
