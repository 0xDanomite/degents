# src/backend/services/token_trend_service.py
from typing import List, Dict, Set
import tweepy
import re
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import os
from dotenv import load_dotenv
from cdp_langchain.utils import CdpAgentkitWrapper

class TokenTrendService:
    def __init__(self):
        load_dotenv()
        # Initialize Twitter client
        self.client = tweepy.Client(
            bearer_token=os.getenv('TWITTER_BEARER_TOKEN'),
            consumer_key=os.getenv('TWITTER_API_KEY'),
            consumer_secret=os.getenv('TWITTER_API_SECRET'),
            access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
            access_token_secret=os.getenv('TWITTER_ACCESS_SECRET'),
            wait_on_rate_limit=True
        )

        # Initialize CDP client
        self.cdp = CdpAgentkitWrapper(
            cdp_api_key_name=os.getenv('CDP_API_KEY_NAME'),
            cdp_api_key_private_key=os.getenv('CDP_API_KEY_PRIVATE_KEY'),
            network_id=os.getenv('NETWORK_ID', 'base-sepolia')
        )

        # Token tracking
        self.token_mentions = defaultdict(list)  # Track mentions over time
        self.known_tokens = set()  # Cache of verified tokens

        # Configuration
        self.min_token_mentions = 5  # Minimum mentions to consider a trend
        self.time_window_minutes = 30  # Time window for trend analysis
        self.max_token_length = 10  # Maximum length for valid token symbols

    async def detect_token_trends(self) -> List[Dict]:
        """Detect trending tokens by monitoring $ mentions"""
        try:
            # Get recent tweets mentioning potential tokens
            tweets = await self._get_token_tweets()
            # Analyze token mentions
            trends = await self._analyze_token_mentions(tweets)
            return trends
        except Exception as e:
            print(f"Error detecting token trends: {e}")
            return []

    async def _get_token_tweets(self) -> List[Dict]:
        """Get recent tweets containing $ symbols"""
        try:
            # Search for tweets with $ mentions
            query = '$ lang:en -is:retweet'  # Basic query for tweets with $ symbol

            tweets = self.client.search_recent_tweets(
                query=query,
                max_results=100,
                tweet_fields=['public_metrics', 'created_at', 'author_id', 'entities']
            )

            processed_tweets = []
            if tweets.data:
                for tweet in tweets.data:
                    # Extract potential token symbols
                    tokens = self._extract_token_symbols(tweet.text)
                    if tokens:  # Only include tweets with token mentions
                        processed_tweets.append({
                            'id': tweet.id,
                            'text': tweet.text,
                            'created_at': tweet.created_at,
                            'metrics': tweet.public_metrics,
                            'tokens': tokens,
                            'author_id': tweet.author_id
                        })

            return processed_tweets

        except Exception as e:
            print(f"Error getting token tweets: {e}")
            return []

    def _extract_token_symbols(self, text: str) -> Set[str]:
        """Extract potential token symbols from tweet text"""
        # Match $SYMBOL pattern
        # Criteria for valid token symbols:
        # 1. Starts with $
        # 2. Followed by 2-10 characters
        # 3. Contains only letters and numbers
        # 4. Must start with a letter
        pattern = r'\$([A-Za-z][A-Za-z0-9]{1,9})'
        matches = re.finditer(pattern, text)
        return {match.group(1).upper() for match in matches}

    async def _verify_token_existence(self, symbol: str) -> Dict:
        """Verify if a token exists on the blockchain"""
        try:
            # Check cache first
            if symbol in self.known_tokens:
                return {"exists": True, "symbol": symbol}

            # Use CDP to check token existence
            # This is a placeholder - implement actual token verification
            token_info = await self._check_token_on_chain(symbol)

            if token_info["exists"]:
                self.known_tokens.add(symbol)

            return token_info

        except Exception as e:
            print(f"Error verifying token {symbol}: {e}")
            return {"exists": False, "symbol": symbol, "error": str(e)}

    async def _check_token_on_chain(self, symbol: str) -> Dict:
        """Check if token exists on the blockchain using CDP"""
        try:
            # Implement CDP token lookup here
            # This is a placeholder for the actual implementation
            return {"exists": False, "symbol": symbol}
        except Exception as e:
            print(f"Error checking token on chain: {e}")
            return {"exists": False, "symbol": symbol, "error": str(e)}

    async def _analyze_token_mentions(self, tweets: List[Dict]) -> List[Dict]:
        """Analyze token mentions and identify trends"""
        try:
            current_time = datetime.now()
            token_stats = defaultdict(lambda: {
                'mentions': 0,
                'unique_users': set(),
                'engagement': 0,
                'recent_tweets': [],
                'first_seen': current_time,
            })

            # Process tweets
            for tweet in tweets:
                for token in tweet['tokens']:
                    stats = token_stats[token]
                    stats['mentions'] += 1
                    stats['unique_users'].add(tweet['author_id'])
                    stats['engagement'] += (
                        tweet['metrics']['retweet_count'] +
                        tweet['metrics']['like_count'] +
                        tweet['metrics']['reply_count']
                    )
                    stats['recent_tweets'].append({
                        'id': tweet['id'],
                        'created_at': tweet['created_at'],
                        'engagement': tweet['metrics']
                    })
                    stats['first_seen'] = min(stats['first_seen'], tweet['created_at'])

            # Calculate trends
            trends = []
            for token, stats in token_stats.items():
                if stats['mentions'] >= self.min_token_mentions:
                    # Verify token existence
                    token_info = await self._verify_token_existence(token)

                    # Calculate trend score
                    trend_score = self._calculate_token_trend_score(stats)

                    trends.append({
                        'symbol': token,
                        'mentions': stats['mentions'],
                        'unique_users': len(stats['unique_users']),
                        'engagement': stats['engagement'],
                        'score': trend_score,
                        'token_verified': token_info.get('exists', False),
                        'first_seen': stats['first_seen'].isoformat(),
                        'timestamp': current_time.isoformat()
                    })

            # Sort by score
            trends.sort(key=lambda x: x['score'], reverse=True)
            return trends

        except Exception as e:
            print(f"Error analyzing token mentions: {e}")
            return []

    def _calculate_token_trend_score(self, stats: Dict) -> float:
        """Calculate trend score based on various metrics"""
        try:
            # Base score from mention count
            mention_score = min(stats['mentions'] / self.min_token_mentions, 2.0)

            # Unique users score
            unique_users_score = len(stats['unique_users']) / max(stats['mentions'], 1)

            # Engagement score
            engagement_per_mention = stats['engagement'] / max(stats['mentions'], 1)
            engagement_score = min(engagement_per_mention / 10, 1.0)

            # Time factor - higher score for more recent activity
            time_factor = 1.0  # Implement time decay if needed

            # Combined score
            total_score = (
                mention_score * 0.4 +
                unique_users_score * 0.3 +
                engagement_score * 0.3
            ) * time_factor

            return round(total_score, 4)

        except Exception as e:
            print(f"Error calculating trend score: {e}")
            return 0.0

    async def get_token_details(self, symbol: str) -> Dict:
        """Get detailed information about a token"""
        try:
            # Verify token exists
            token_info = await self._verify_token_existence(symbol)

            if not token_info['exists']:
                return {
                    'symbol': symbol,
                    'exists': False,
                    'message': 'Token not found'
                }

            # Get additional token information
            # Implement CDP token details lookup here

            return token_info

        except Exception as e:
            print(f"Error getting token details: {e}")
            return {
                'symbol': symbol,
                'exists': False,
                'error': str(e)
            }
