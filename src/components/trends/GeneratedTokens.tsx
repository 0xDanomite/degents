import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Brain,
  Rocket,
  CheckCircle,
  ExternalLink,
} from 'lucide-react';
import { getBaseScanUrl } from '@/lib/utils';

interface GeneratedToken {
  name: string;
  symbol: string;
  description: string;
  initial_supply: number;
  max_supply: number;
  source_trends: {
    symbol: string;
    score: number;
  }[];
  created?: boolean;
  transaction_hash?: string;
}

interface GeneratedTokensProps {
  tokens: GeneratedToken[];
  onCreateToken: (token: GeneratedToken) => void;
  isAutoTrading: boolean;
}

export const GeneratedTokens = ({
  tokens,
  onCreateToken,
  isAutoTrading,
}: GeneratedTokensProps) => {
  const formatSupply = (supply: number) => {
    return new Intl.NumberFormat().format(supply);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Brain className="h-5 w-5" />
          Generated Meme Tokens
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {tokens.length === 0 ? (
            <p className="text-center text-muted-foreground">
              No tokens generated yet
            </p>
          ) : (
            tokens.map((token, index) => (
              <div
                key={index}
                className="border rounded-lg p-4 space-y-3"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-bold flex items-center gap-2">
                      {token.name}
                      <Badge variant="secondary">
                        {token.symbol}
                      </Badge>
                    </h3>
                    <p className="text-sm text-muted-foreground">
                      Supply: {formatSupply(token.initial_supply)} /{' '}
                      {formatSupply(token.max_supply)}
                    </p>
                  </div>
                  {token.created ? (
                    <div className="flex items-center gap-2">
                      <Badge
                        variant="success"
                        className="flex items-center gap-1"
                      >
                        <CheckCircle className="h-3 w-3" />
                        Created
                      </Badge>
                      {token.transaction_hash && (
                        <a
                          href={getBaseScanUrl(
                            token.transaction_hash,
                            token?.network || 'base-sepolia'
                          )}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-500 hover:text-blue-600"
                        >
                          <ExternalLink className="h-4 w-4" />
                        </a>
                      )}
                    </div>
                  ) : (
                    <Button
                      onClick={() => onCreateToken(token)}
                      className="flex items-center gap-2"
                      disabled={isAutoTrading}
                    >
                      <Rocket className="h-4 w-4" />
                      {isAutoTrading
                        ? 'Auto-Creating...'
                        : 'Create Token'}
                    </Button>
                  )}
                </div>

                <p className="text-sm">{token.description}</p>

                <div className="flex gap-2">
                  {token.source_trends.map((trend, i) => (
                    <Badge key={i} variant="outline">
                      ${trend.symbol} ({trend.score.toFixed(2)})
                    </Badge>
                  ))}
                </div>
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
};
