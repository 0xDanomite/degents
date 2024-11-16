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
