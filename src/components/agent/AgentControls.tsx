import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Switch } from '@/components/ui/switch';
import { Button } from '@/components/ui/button';
import { Brain, Play, Pause } from 'lucide-react';

export const AgentControls = ({
  isRunning,
  autoTrading,
  onToggleAgent,
  onToggleAutoTrading,
}) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Brain className="h-5 w-5" />
          Agent Controls
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <span>Agent Status</span>
          <Button
            onClick={onToggleAgent}
            variant={isRunning ? 'destructive' : 'default'}
            className="flex items-center gap-2"
          >
            {isRunning ? (
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
            onCheckedChange={onToggleAutoTrading}
          />
        </div>
      </CardContent>
    </Card>
  );
};
