'use client';

import { useEffect, useState } from 'react';
import { ActivityFeed } from '@/components/agent/ActivityFeed';
import { FundManagement } from '@/components/agent/FundManagement';
import { AgentControls } from '@/components/agent/AgentControls';
import { TrendList } from '@/components/trends/TrendList';
import { TrendAnalysis } from '@/components/trends/TrendAnalysis';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface TokenTrend {
  symbol: string;
  mentions: number;
  score: number;
  token_verified: boolean;
  engagement: number;
}

interface Analysis {
  symbol: string;
  analysis: string;
  action: string;
  transaction?: string;
}

interface WalletInfo {
  address: string;
  balance: string;
  network: string;
}

export default function TokenDashboard() {
  // State management
  const [tokenTrends, setTokenTrends] = useState<TokenTrend[]>([]);
  const [walletInfo, setWalletInfo] = useState<WalletInfo | null>(
    null
  );
  const [holdings, setHoldings] = useState([]);
  const [isAgentRunning, setIsAgentRunning] = useState(false);
  const [autoTrading, setAutoTrading] = useState(false);
  const [status, setStatus] = useState('');
  const [error, setError] = useState('');
  const [analysis, setAnalysis] = useState<Analysis | null>(null);

  // Fetch functions
  const fetchTokenTrends = async () => {
    try {
      const response = await fetch('/api/token-trends');
      const data = await response.json();
      if (data.trends) {
        setTokenTrends(data.trends);
      } else {
        throw new Error('Failed to fetch trends.');
      }
    } catch (err) {
      setError('Error fetching trends: ' + err.message);
    }
  };

  const fetchWalletInfo = async () => {
    try {
      const response = await fetch('/api/wallet');
      const data = await response.json();
      setWalletInfo(data);
    } catch (err) {
      setError('Error fetching wallet info');
    }
  };

  const fetchHoldings = async () => {
    try {
      const response = await fetch('/api/holdings');
      const data = await response.json();
      setHoldings(data.holdings);
    } catch (err) {
      setError('Error fetching holdings');
    }
  };

  const analyzeToken = async (token: TokenTrend) => {
    try {
      setStatus(`Analyzing ${token.symbol}...`);
      const response = await fetch('/api/analyze-token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(token),
      });
      const data = await response.json();
      setAnalysis(data);
      setStatus(`Analysis complete for ${token.symbol}`);
    } catch (err) {
      setError('Error analyzing token');
    }
  };

  const toggleAutoTrading = async (checked: boolean) => {
    try {
      const response = await fetch('/api/agent/auto-trading', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled: checked }),
      });
      const data = await response.json();
      setAutoTrading(checked);
      setStatus(`Auto Trading ${checked ? 'enabled' : 'disabled'}`);
    } catch (err) {
      setError('Failed to toggle auto trading');
    }
  };

  const toggleAgent = async () => {
    try {
      const action = isAgentRunning ? 'stop' : 'start';
      const response = await fetch(`/api/agent/${action}`, {
        method: 'POST',
      });
      const data = await response.json();
      setIsAgentRunning(!isAgentRunning);
      setStatus(`Agent ${action}ed successfully`);
    } catch (err) {
      setError(
        `Failed to ${isAgentRunning ? 'stop' : 'start'} agent`
      );
    }
  };

  // Initial load and polling
  useEffect(() => {
    fetchTokenTrends();
    fetchWalletInfo();
    fetchHoldings();

    // Set up polling for updates
    const interval = setInterval(() => {
      fetchTokenTrends();
      fetchWalletInfo();
      fetchHoldings();
    }, 30000); // Update every 30 seconds

    return () => clearInterval(interval);
  }, []);

  // WebSocket connection
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws');

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'token_update') {
        setTokenTrends((prevTrends) => {
          const updatedTrends = [...prevTrends];
          const index = updatedTrends.findIndex(
            (t) => t.symbol === data.token.symbol
          );
          if (index !== -1) {
            updatedTrends[index] = data.token;
          } else {
            updatedTrends.push(data.token);
          }
          return updatedTrends;
        });
      }
    };

    return () => ws.close();
  }, []);

  return (
    <main className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">
        Token Trend Dashboard
      </h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <AgentControls
          isRunning={isAgentRunning}
          autoTrading={autoTrading}
          onToggleAgent={toggleAgent}
          onToggleAutoTrading={toggleAutoTrading}
        />
        <FundManagement />
      </div>

      <div className="grid grid-cols-1 gap-4">
        <ActivityFeed />
        <TrendList trends={tokenTrends} onAnalyze={analyzeToken} />
        {analysis && <TrendAnalysis analysis={analysis} />}
      </div>

      {/* Status and Error Alerts */}
      {status && (
        <Alert className="mt-4">
          <AlertDescription>{status}</AlertDescription>
        </Alert>
      )}
      {error && (
        <Alert variant="destructive" className="mt-4">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
    </main>
  );
}
