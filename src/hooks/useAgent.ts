// src/hooks/useAgent.ts
import { useState, useEffect, useRef } from 'react';
import { AgentState } from '@/types/agent';

const API_BASE_URL = 'http://localhost:8000';

export function useAgent() {
  const [state, setState] = useState<AgentState | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Initialize WebSocket connection
    wsRef.current = new WebSocket('ws://localhost:8000/ws/agent');

    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === 'state_update') {
        setState(data.state);
      } else if (
        data.type === 'agent_thought' ||
        data.type === 'agent_action'
      ) {
        // Handle agent updates - could update a separate state for agent activities
        console.log('Agent update:', data);
      } else if (data.type === 'error') {
        setError(data.content);
      }
    };

    wsRef.current.onerror = (error) => {
      console.error('WebSocket error:', error);
      setError('WebSocket connection error');
    };

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const controlAgent = async (action: string, payload?: any) => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/agent/${action}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        }
      );

      const data = await response.json();

      if (!data.state) {
        throw new Error(data.error || 'Failed to control agent');
      }

      setState(data.state);
      return data;
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Failed to control agent'
      );
      throw err;
    }
  };

  return {
    state,
    loading,
    error,
    startAgent: () => controlAgent('start'),
    stopAgent: () => controlAgent('stop'),
    setAutoTrading: (enabled: boolean) =>
      controlAgent('auto-trading', { enabled }),
  };
}
