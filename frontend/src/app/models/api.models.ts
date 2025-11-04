// API Models matching backend and LLM service

export interface Period {
  start: string;
  end: string;
  days: number;
}

export interface SeriesItem {
  name: string;
  data: number[];
}

export interface TimeseriesResponse {
  period: Period;
  keywords: string[];
  dates: string[];
  series: SeriesItem[];
}

export interface CompareResponse {
  period: Period;
  keywords: string[];
  dates: string[];
  series: SeriesItem[];
  meta: {
    normalized: boolean;
    cumulative: boolean;
    smooth: number;
  };
}

// LLM Service Models
export interface ProviderOutput {
  provider: string;
  model: string;
  summary: string;
  actions_short: string[];
  actions_mid: string[];
  actions_long: string[];
  confidence: number;
}

export interface TrendResponse {
  period: Period;
  top_keywords: string[];
  dates: string[];
  provider_outputs: ProviderOutput[];
  consensus_summary: string;
  notes?: string;
}

export interface TrendRequest {
  period: Period;
  top_keywords: string[];
  dates: string[];
  series: SeriesItem[];
  output_lang?: string;
  short_mid_long_base_days?: number;
  mode?: string;
  use_cache?: boolean;
}

export interface DateRange {
  start: Date;
  end: Date;
}
