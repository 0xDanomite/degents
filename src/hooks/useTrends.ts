// src/hooks/useTrends.ts
import { useState, useEffect } from 'react';
import { ProcessedTrend } from '@/types/trends';

export function useTrends() {
  const [trends, setTrends] = useState<ProcessedTrend[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTrends = async () => {
      try {
        const response = await fetch('/api/trends');
        const data = await response.json();

        if (!data.success) {
          throw new Error(data.error);
        }

        setTrends(data.trends);
        setError(null);
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : 'Failed to fetch trends'
        );
      } finally {
        setLoading(false);
      }
    };

    fetchTrends();
    const interval = setInterval(fetchTrends, 5 * 60 * 1000); // Update every 5 minutes

    return () => clearInterval(interval);
  }, []);

  return { trends, loading, error };
}
