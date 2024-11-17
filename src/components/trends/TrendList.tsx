import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { TrendingUp, CheckCircle, XCircle } from 'lucide-react';

interface TrendToken {
  symbol: string;
  mentions: number;
  score: number;
  token_verified: boolean;
  engagement: number;
}

interface TrendListProps {
  trends: TrendToken[];
  onAnalyze: (trend: TrendToken) => void;
}

export const TrendList = ({ trends, onAnalyze }: TrendListProps) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <TrendingUp className="h-5 w-5" />
          Trending Tokens
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {trends.map((token, index) => (
            <div
              key={index}
              className="p-3 border rounded-lg flex items-center justify-between hover:bg-gray-50"
            >
              <div className="flex items-center gap-4">
                <span className="font-medium">${token.symbol}</span>
                {token.token_verified ? (
                  <Badge
                    variant="default"
                    className="flex items-center gap-1"
                  >
                    <CheckCircle className="h-3 w-3" />
                    Verified
                  </Badge>
                ) : (
                  <Badge
                    variant="secondary"
                    className="flex items-center gap-1"
                  >
                    <XCircle className="h-3 w-3" />
                    Unverified
                  </Badge>
                )}
              </div>
              <div className="flex items-center gap-6">
                <div className="text-sm grid grid-cols-2 gap-x-2">
                  <span className="text-gray-500">Mentions:</span>
                  <span className="font-medium">
                    {token.mentions}
                  </span>
                  <span className="text-gray-500">Score:</span>
                  <span className="font-medium">
                    {token.score.toFixed(2)}
                  </span>
                </div>
                <Button
                  onClick={() => onAnalyze(token)}
                  variant="outline"
                  size="sm"
                >
                  Analyze
                </Button>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};
