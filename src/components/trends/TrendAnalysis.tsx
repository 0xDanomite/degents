import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Search } from 'lucide-react';

interface Analysis {
  symbol: string;
  analysis: string;
  action: string;
  transaction?: string;
}

interface TrendAnalysisProps {
  analysis: Analysis | null;
}

export const TrendAnalysis = ({ analysis }: TrendAnalysisProps) => {
  if (!analysis) return null;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Search className="h-5 w-5" />
          Analysis Result
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          <div className="font-medium">Token: ${analysis.symbol}</div>
          <div className="text-sm whitespace-pre-wrap">
            {analysis.analysis}
          </div>
          {analysis.action === 'buy' && analysis.transaction && (
            <Alert>
              <AlertDescription>
                Trade executed! Transaction: {analysis.transaction}
              </AlertDescription>
            </Alert>
          )}
        </div>
      </CardContent>
    </Card>
  );
};
