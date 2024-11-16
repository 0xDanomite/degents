// src/app/page.tsx
'use client';

import { useState } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Play, Pause, AlertCircle } from 'lucide-react';

export default function TestDashboard() {
  const [isAgentRunning, setIsAgentRunning] = useState(false);
  const [autoTrading, setAutoTrading] = useState(false);
  const [status, setStatus] = useState<string>('');
  const [error, setError] = useState<string | null>(null);

  const handleAgentControl = async (action: 'start' | 'stop') => {
    try {
      const response = await fetch(`/api/agent/${action}`, {
        method: 'POST',
      });
      const data = await response.json();
      setStatus(`Agent ${action}ed successfully`);
      setIsAgentRunning(action === 'start');
      setError(null);
    } catch (err) {
      setError(`Failed to ${action} agent`);
    }
  };

  const handleAutoTradingToggle = async () => {
    try {
      const newState = !autoTrading;
      const response = await fetch('/api/agent/auto-trading', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ enabled: newState }),
      });
      const data = await response.json();
      setAutoTrading(newState);
      setStatus(`Auto-trading ${newState ? 'enabled' : 'disabled'}`);
      setError(null);
    } catch (err) {
      setError('Failed to toggle auto-trading');
    }
  };

  return (
    <main className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">
        Agent Test Dashboard
      </h1>

      {/* Controls Card */}
      <Card className="mb-4">
        <CardHeader>
          <CardTitle>Agent Controls</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <span>Agent Status</span>
            <Button
              onClick={() =>
                handleAgentControl(isAgentRunning ? 'stop' : 'start')
              }
              variant={isAgentRunning ? 'destructive' : 'default'}
              className="flex items-center gap-2"
            >
              {isAgentRunning ? (
                <>
                  <Pause className="h-4 w-4" /> Stop Agent
                </>
              ) : (
                <>
                  <Play className="h-4 w-4" /> Start Agent
                </>
              )}
            </Button>
          </div>

          <div className="flex items-center justify-between">
            <span>Auto Trading</span>
            <Switch
              checked={autoTrading}
              onCheckedChange={handleAutoTradingToggle}
            />
          </div>
        </CardContent>
      </Card>

      {/* Status Messages */}
      {status && (
        <Alert className="mb-4">
          <AlertDescription>{status}</AlertDescription>
        </Alert>
      )}

      {/* Error Messages */}
      {error && (
        <Alert variant="destructive" className="mb-4">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
    </main>
  );
}
