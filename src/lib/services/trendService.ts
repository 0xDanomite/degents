// src/lib/services/trends.ts
import { TwitterService } from './twitterService';
import { ProcessedTrend, TrendServiceError } from '@/types/trends';

export class TrendService {
  private twitterService: TwitterService;
  private cache: Map<string, ProcessedTrend>;
  private lastUpdate: Date;
  private readonly UPDATE_INTERVAL = 5 * 60 * 1000; // 5 minutes

  constructor() {
    this.twitterService = new TwitterService();
    this.cache = new Map();
    this.lastUpdate = new Date(0); // Initialize to past date
  }

  async getTrends(): Promise<ProcessedTrend[]> {
    try {
      // Check if we need to update the cache
      if (this.shouldUpdateCache()) {
        await this.updateTrends();
      }

      // Return sorted trends
      return Array.from(this.cache.values()).sort(
        (a, b) => b.score - a.score
      );
    } catch (error) {
      const serviceError: TrendServiceError = {
        message:
          error instanceof Error
            ? error.message
            : 'Error fetching trends',
        code: 'TREND_SERVICE_ERROR',
        source: 'TrendService',
      };

      console.error('Trend Service Error:', serviceError);
      throw serviceError;
    }
  }

  private async updateTrends(): Promise<void> {
    try {
      // Get Twitter trends
      const twitterTrends = await this.twitterService.getTrends();

      // Process each trend
      for (const trend of twitterTrends) {
        const processedTrend: ProcessedTrend = {
          id: `twitter-${trend.name}`,
          name: trend.name,
          source: 'twitter',
          volume: trend.tweet_volume || 0,
          score: this.calculateTrendScore(trend),
          timestamp: new Date().toISOString(),
          metadata: {
            query: trend.query,
            url: trend.url,
          },
        };

        this.cache.set(processedTrend.id, processedTrend);
      }

      this.lastUpdate = new Date();
    } catch (error) {
      console.error('Error updating trends:', error);
      throw error;
    }
  }

  private calculateTrendScore(trend: {
    tweet_volume: number | null;
  }): number {
    if (!trend.tweet_volume) return 0;

    // Basic scoring algorithm - can be enhanced
    const volumeScore = Math.min(trend.tweet_volume / 10000, 1); // Normalize to 0-1

    // You can add more factors to the scoring:
    // - Growth rate
    // - Engagement metrics
    // - Age of trend
    // - Geographic spread
    // - Sentiment analysis

    return volumeScore;
  }

  private shouldUpdateCache(): boolean {
    const now = new Date();
    return (
      now.getTime() - this.lastUpdate.getTime() > this.UPDATE_INTERVAL
    );
  }
}
