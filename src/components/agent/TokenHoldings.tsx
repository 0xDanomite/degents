import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Coins } from 'lucide-react';

interface TokenHolding {
  symbol: string;
  balance: string;
  token_address: string;
}

interface TokenHoldingsProps {
  holdings: TokenHolding[];
}

export const TokenHoldings = ({ holdings }: TokenHoldingsProps) => {
  const shortenAddress = (addr: string) => {
    if (addr === 'native') return 'Native';
    return `${addr.slice(0, 6)}...${addr.slice(-4)}`;
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Coins className="h-5 w-5" />
          Token Holdings
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {holdings.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-4">
              No tokens found
            </p>
          ) : (
            holdings.map((token, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-2 border rounded-lg"
              >
                <div className="flex items-center gap-2">
                  <span className="font-medium">{token.symbol}</span>
                  <Badge variant="outline" className="text-xs">
                    {shortenAddress(token.token_address)}
                  </Badge>
                </div>
                <span className="text-sm">{token.balance}</span>
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
};
