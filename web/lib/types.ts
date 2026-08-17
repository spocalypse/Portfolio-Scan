/** Shapes mirrored from fixtures/metrics.sample.json (AnalyzeResponse). Do not invent fields. */

export type Severity = "info" | "notable";

export type PositionWeight = {
  ticker: string;
  sector: string;
  capital_weight: number;
};

export type SectorExposure = {
  sector: string;
  capital_weight: number;
  risk_contribution_pct: number;
};

export type SectorCapital = {
  sector: string;
  capital_weight: number;
};

export type RiskContribution = {
  ticker: string;
  weight: number;
  mcr: number;
  rc: number;
  rc_pct: number;
};

export type FactorLoading = {
  factor: string;
  loading: number;
  t_stat: number;
  significant: boolean;
};

export type PairwiseOverlap = {
  etf_a: string;
  etf_b: string;
  overlap_pct: number;
};

export type LookThroughWeight = {
  ticker: string;
  true_weight: number;
};

export type ExcludedHolding = {
  ticker: string;
  reason: string;
  detail: string;
};

export type Finding = {
  headline: string;
  explanation: string;
  severity: Severity;
  metrics_referenced: string[];
};

export type AnalyzeMeta = {
  request_id: string;
  computed_at: string;
  data_window_days: number;
  price_data_as_of: string;
  price_data_stale: boolean;
  narrative_model_used: string;
  warnings: string[];
};

export type Metrics = {
  m1_weights: {
    position_weights: PositionWeight[];
    sector_exposure: SectorExposure[];
    top_sector_concentration: SectorCapital[];
    hhi: number;
    effective_position_count: number;
  };
  m2_beta: {
    beta: number;
    r_squared: number;
  };
  m3_risk_contribution: {
    portfolio_volatility: number;
    contributions: RiskContribution[];
  };
  m4_effective_bets: {
    effective_number_of_bets: number;
    naive_position_count: number;
  };
  m5_factor_tilts: {
    loadings: FactorLoading[];
    r_squared: number;
  };
  m6_etf_look_through: {
    snapshot_date: string;
    etfs_detected: string[];
    pairwise_overlap: PairwiseOverlap[];
    look_through_weights: LookThroughWeight[];
  };
  excluded_holdings: ExcludedHolding[];
};

export type AnalyzeResponse = {
  metrics: Metrics;
  findings: Finding[];
  meta: AnalyzeMeta;
};
