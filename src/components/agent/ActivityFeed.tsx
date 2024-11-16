import { useEffect, useState } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import {
  Activity,
  Info,
  Search,
  DollarSign,
  AlertTriangle,
  XCircle,
  CheckCircle,
} from 'lucide-react';

export const ActivityFeed = () => {
  const [activities, setActivities] = useState([]);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws');

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'agent_activity') {
        setActivities((prev) => [data.data, ...prev].slice(0, 50)); // Keep last 50 activities
      }
    };

    return () => ws.close();
  }, []);

  const getActivityIcon = (type) => {
    switch (type) {
      case 'info':
        return <Info className="h-4 w-4" />;
      case 'analysis':
        return <Search className="h-4 w-4" />;
      case 'trade':
        return <DollarSign className="h-4 w-4" />;
      case 'warning':
        return <AlertTriangle className="h-4 w-4" />;
      case 'error':
        return <XCircle className="h-4 w-4" />;
      case 'success':
        return <CheckCircle className="h-4 w-4" />;
      default:
        return null;
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Activity className="h-5 w-5" />
          Agent Activity
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4 max-h-96 overflow-y-auto">
          {activities.map((activity, index) => (
            <div
              key={index}
              className="flex items-start gap-2 p-2 border rounded"
            >
              <div
                className={`mt-1 ${
                  activity.type === 'error'
                    ? 'text-red-500'
                    : activity.type === 'success'
                    ? 'text-green-500'
                    : activity.type === 'warning'
                    ? 'text-yellow-500'
                    : 'text-blue-500'
                }`}
              >
                {getActivityIcon(activity.type)}
              </div>
              <div className="flex-1">
                <p className="text-sm">{activity.message}</p>
                {activity.details && (
                  <pre className="mt-1 text-xs text-gray-500 whitespace-pre-wrap">
                    {JSON.stringify(activity.details, null, 2)}
                  </pre>
                )}
                <span className="text-xs text-gray-400">
                  {new Date(activity.timestamp).toLocaleTimeString()}
                </span>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};
