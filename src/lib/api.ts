import { TokenTrend, AgentState } from '@/types/token';

export const api = {
  async getTokenTrends(): Promise<TokenTrend[]> {
    const response = await fetch('/api/token-trends');
    const data = await response.json();
    return data.trends;
  },

  async controlAgent(action: 'start' | 'stop'): Promise<AgentState> {
    const response = await fetch(`/api/agent/${action}`, {
      method: 'POST',
    });
    const data = await response.json();
    return data.state;
  },

  async processToken(token: TokenTrend): Promise<any> {
    const response = await fetch('/api/agent/process-token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(token),
    });
    return response.json();
  },
};
