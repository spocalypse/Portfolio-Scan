import { AppShell } from "@/components/AppShell";
import { loadSampleExtract } from "@/lib/load-extract-sample";
import { loadSampleAnalyze } from "@/lib/load-fixture";

export default function Home() {
  const analyzeFixture = loadSampleAnalyze();
  const extractSample = loadSampleExtract();

  return <AppShell analyzeFixture={analyzeFixture} extractSample={extractSample} />;
}
