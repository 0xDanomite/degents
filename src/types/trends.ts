// src/types/trends.ts
export interface TwitterTrend {
  name: string;
  query: string;
  tweet_volume: number | null;
  url: string;
}

export interface ProcessedTrend {
  id: string;
  name: string;
  source: 'twitter' | 'tiktok';
  volume: number;
  score: number;
  timestamp: string;
  metadata: {
    query?: string;
    url?: string;
    rank?: number;
  };
}

export interface TrendServiceError {
  message: string;
  code: string;
  source: string;
}
