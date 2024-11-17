'use client';

import { useEffect, useState } from 'react';
import { ActivityFeed } from '@/components/agent/ActivityFeed';
// import { FundManagement } from '@/components/agent/FundManagement';
import { AgentControls } from '@/components/agent/AgentControls';
import { TrendList } from '@/components/trends/TrendList';
import { TrendAnalysis } from '@/components/trends/TrendAnalysis';
import { WalletInfo } from '@/components/agent/WalletInfo';
import { TokenHoldings } from '@/components/agent/TokenHoldings';
import { Alert, AlertDescription } from '@/components/ui/alert';
// import { MemeCombinations } from '@/components/trends/MemeCombinations';
import { GeneratedTokens } from '@/components/trends/GeneratedTokens';
import { GeneratedToken, MemeCombination } from '@/types/token';

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

interface TokenHolding {
  symbol: string;
  balance: string;
  token_address: string;
  last_updated: string;
}

export default function TokenDashboard() {
  // State management
  const [tokenTrends, setTokenTrends] = useState<TokenTrend[]>([]);
  const [walletInfo, setWalletInfo] = useState<WalletInfo>({
    address: 'Loading...',
    balance: '0',
    network: 'Loading...',
  });
  const [holdings, setHoldings] = useState<TokenHolding[]>([]);
  const [isAgentRunning, setIsAgentRunning] = useState(false);
  const [autoTrading, setAutoTrading] = useState(false);
  const [status, setStatus] = useState('');
  const [error, setError] = useState('');
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  // const [memeCombinations, setMemeCombinations] = useState<
  //   MemeCombination[]
  // >([]);
  const [generatedTokens, setGeneratedTokens] = useState<
    GeneratedToken[]
  >([]);

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
      setError(
        'Error fetching trends: ' +
          (err instanceof Error ? err.message : String(err))
      );
    }
  };

  const fetchWalletInfo = async () => {
    try {
      const response = await fetch('/api/wallet');
      const data = await response.json();
      setWalletInfo(data);
    } catch (err) {
      setError('Error fetching wallet info');
      console.error('Wallet fetch error:', err);
    }
  };

  const fetchHoldings = async () => {
    try {
      const response = await fetch('/api/holdings');
      const data = await response.json();
      setHoldings(data.holdings || []);
    } catch (err) {
      setError('Error fetching holdings');
      console.error('Holdings fetch error:', err);
    }
  };

  // const fetchMemeCombinations = async () => {
  //   try {
  //     const response = await fetch('/api/meme-combinations');
  //     const data = await response.json();
  //     if (data.success) {
  //       setMemeCombinations(data.combinations);
  //     }
  //   } catch (err) {
  //     setError('Error fetching meme combinations');
  //   }
  // };

  const fetchGeneratedTokens = async () => {
    try {
      const response = await fetch('/api/generated-tokens');
      const data = await response.json();
      setGeneratedTokens(data.tokens || []);
    } catch (err) {
      setError('Error fetching generated tokens');
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
      console.error('Analysis error:', err);
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
      console.error('Auto trading toggle error:', err);
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
      console.error('Agent toggle error:', err);
    }
  };

  const createMemeToken = async (combination: MemeCombination) => {
    try {
      setStatus(`Creating token ${combination.symbol}...`);
      const response = await fetch('/api/create-meme-token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(combination),
      });
      const data = await response.json();
      setStatus(`Successfully created token ${combination.symbol}!`);
    } catch (err) {
      setError('Error creating meme token');
    }
  };

  // Initial load and polling
  useEffect(() => {
    const fetchData = async () => {
      await Promise.all([
        fetchTokenTrends(),
        fetchWalletInfo(),
        fetchHoldings(),
        fetchGeneratedTokens(),
      ]);
    };

    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  // WebSocket connection for real-time updates
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws');

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'agent_activity') {
        // Handle agent activity updates
        setStatus(data.data.message);
        // Refresh data if needed
        fetchWalletInfo();
        fetchHoldings();
      }
    };

    return () => ws.close();
  }, []);

  return (
    <main className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">
        Degents Dashboard - AI Agents for Degens
      </h1>

      {/* First Row: Wallet Info and Agent Controls */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <WalletInfo
          address={walletInfo.address}
          balance={walletInfo.balance}
          network={walletInfo.network}
        />
        <AgentControls
          isRunning={isAgentRunning}
          autoTrading={autoTrading}
          onToggleAgent={toggleAgent}
          onToggleAutoTrading={toggleAutoTrading}
        />
      </div>

      {/* Second Row: Token Holdings and Fund Management */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <TokenHoldings holdings={holdings} />
        {/* <FundManagement /> */}
      </div>

      {/* Activity Feed and Trends */}
      <div className="grid grid-cols-1 gap-4">
        {/* <MemeCombinations
          combinations={memeCombinations}
          onCreateToken={createMemeToken}
        /> */}
        <GeneratedTokens
          tokens={generatedTokens}
          onCreateToken={() => createMemeToken}
          isAutoTrading={autoTrading}
        />
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
