import { ProcessedTrend } from './trends';

export interface TokenPosition {
  address: string;
  symbol: string;
  name: string;
  trend: string;
  amount: number;
  entryPrice: number;
  currentPrice: number;
  pnl: number;
  timestamp: string;
}

export interface AgentState {
  isRunning: boolean;
  autoTrading: boolean;
  lastUpdate: string;
  activeTrends: ProcessedTrend[];
  activeTokens: TokenPosition[];
  performance: {
    totalPnl: number;
    successRate: number;
    totalTrades: number;
  };
}

export interface AgentConfig {
  minTrendScore: number;
  maxPositions: number;
  maxInvestmentPerTrade: number;
  stopLossPercentage: number;
  takeProfitPercentage: number;
  riskThreshold: number;
}

export type AgentEvent =
  | { type: 'TREND_DETECTED'; payload: ProcessedTrend }
  | { type: 'POSITION_OPENED'; payload: TokenPosition }
  | { type: 'POSITION_CLOSED'; payload: TokenPosition }
  | { type: 'ERROR'; payload: Error }
  | { type: 'STATE_UPDATED'; payload: AgentState };
