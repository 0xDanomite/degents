// // src/lib/services/twitter.ts
// import { TwitterApi } from 'twitter-api-v2';
// import { TwitterTrend, TrendServiceError } from '@/types/trends';

// export class TwitterService {
//   private client: TwitterApi;
//   private readonly WORLDWIDE_WOEID = 1; // Twitter's worldwide location ID

//   constructor() {
//     // Validate environment variables first
//     this.validateEnvVariables();

//     this.client = new TwitterApi({
//       appKey: process.env.TWITTER_API_KEY!,
//       appSecret: process.env.TWITTER_API_SECRET!,
//       accessToken: process.env.TWITTER_ACCESS_TOKEN!,
//       accessSecret: process.env.TWITTER_ACCESS_SECRET!,
//     });
//   }

//   private validateEnvVariables() {
//     const requiredVars = [
//       'TWITTER_API_KEY',
//       'TWITTER_API_SECRET',
//       'TWITTER_ACCESS_TOKEN',
//       'TWITTER_ACCESS_SECRET',
//       'TWITTER_BEARER_TOKEN',
//     ];

//     const missing = requiredVars.filter(
//       (varName) => !process.env[varName]
//     );

//     if (missing.length > 0) {
//       throw new Error(
//         `Missing required Twitter environment variables: ${missing.join(
//           ', '
//         )}`
//       );
//     }
//   }

//   async getTrends(): Promise<TwitterTrend[]> {
//     try {
//       const trends = await this.client.v1.trendsByPlace(
//         this.WORLDWIDE_WOEID
//       );

//       // The API response contains an array with a trends property
//       const [trendData] = trends;

//       return trendData.trends.map((trend) => ({
//         name: trend.name,
//         query: trend.query,
//         tweet_volume: trend.tweet_volume,
//         url: trend.url,
//       }));
//     } catch (error) {
//       const serviceError: TrendServiceError = {
//         message:
//           error instanceof Error
//             ? error.message
//             : 'Unknown Twitter API error',
//         code: 'TWITTER_API_ERROR',
//         source: 'TwitterService',
//       };

//       console.error('Twitter API Error:', serviceError);
//       throw serviceError;
//     }
//   }

//   async getTrendDetails(trendName: string) {
//     try {
//       // Get recent tweets for trend analysis
//       const tweets = await this.client.v2.search({
//         query: trendName,
//         max_results: 100,
//         'tweet.fields': ['public_metrics', 'created_at'],
//       });

//       return tweets;
//     } catch (error) {
//       const serviceError: TrendServiceError = {
//         message:
//           error instanceof Error
//             ? error.message
//             : 'Error fetching trend details',
//         code: 'TWITTER_TREND_DETAILS_ERROR',
//         source: 'TwitterService',
//       };

//       console.error('Twitter Trend Details Error:', serviceError);
//       throw serviceError;
//     }
//   }
// }
