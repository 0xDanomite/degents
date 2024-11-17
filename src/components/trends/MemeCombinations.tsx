import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Brain, Rocket, Sparkles } from 'lucide-react';

interface MemeCombination {
  name: string;
  symbol: string;
  description: string;
  tagline: string;
  meme_potential: string;
  source_trends: {
    symbol: string;
    score: number;
  }[];
}

interface MemeCombinationsProps {
  combinations: MemeCombination[];
  onCreateToken: (combination: MemeCombination) => void;
  isLoading?: boolean;
}

export const MemeCombinations = ({
  combinations,
  onCreateToken,
  isLoading,
}: MemeCombinationsProps) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Brain className="h-5 w-5" />
          AI-Generated Meme Combinations
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {combinations.length === 0 ? (
            <p className="text-center text-muted-foreground">
              {isLoading
                ? 'Generating meme combinations...'
                : 'No meme combinations generated yet'}
            </p>
          ) : (
            combinations.map((combo, index) => (
              <div
                key={index}
                className="border rounded-lg p-4 space-y-3"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-bold flex items-center gap-2">
                      {combo.name}
                      <Badge variant="secondary">
                        ${combo.symbol}
                      </Badge>
                    </h3>
                    <p className="text-sm text-muted-foreground italic">
                      {combo.tagline}
                    </p>
                  </div>
                  <Button
                    onClick={() => onCreateToken(combo)}
                    className="flex items-center gap-2"
                  >
                    <Rocket className="h-4 w-4" />
                    Create Token
                  </Button>
                </div>

                <p className="text-sm">{combo.description}</p>

                <div className="text-sm space-y-1">
                  <div className="flex items-center gap-1 text-muted-foreground">
                    <Sparkles className="h-4 w-4" />
                    Meme Potential:
                  </div>
                  <p>{combo.meme_potential}</p>
                </div>

                <div className="flex gap-2">
                  {combo.source_trends.map((trend, i) => (
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
