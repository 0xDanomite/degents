export interface TokenTrend {
  symbol: string;
  mentions: number;
  unique_users: number;
  engagement: number;
  score: number;
  token_verified: boolean;
  first_seen: string;
  timestamp: string;
}

export interface AgentState {
  is_running: boolean;
  auto_trading: boolean;
  active_tokens: TokenTrend[];
  last_update: string;
}

export interface GeneratedToken {
  name: string;
  symbol: string;
  description: string;
  initial_supply: number;
  max_supply: number;
  source_trends: {
    symbol: string;
    score: number;
  }[];
  created?: boolean;
  transaction_hash?: string;
  network: string;
}
