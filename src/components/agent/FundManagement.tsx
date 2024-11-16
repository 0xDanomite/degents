import { useState } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { toast } from '@/hooks/use-toast';

export const FundManagement = () => {
  const [amount, setAmount] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);

  const handleFunds = async (action) => {
    try {
      setIsProcessing(true);
      const response = await fetch('/api/wallet/manage-funds', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, amount: parseFloat(amount) }),
      });
      const data = await response.json();
      toast.success(`Successfully ${action}ed ${amount} ETH`);
      setAmount('');
    } catch (error) {
      toast.error(`Failed to ${action} funds`);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Fund Management</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex gap-4">
            <Input
              type="number"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              placeholder="Amount in ETH"
            />
            <Button
              onClick={() => handleFunds('deposit')}
              disabled={isProcessing || !amount}
            >
              Deposit
            </Button>
            <Button
              onClick={() => handleFunds('withdraw')}
              disabled={isProcessing || !amount}
              variant="outline"
            >
              Withdraw
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
