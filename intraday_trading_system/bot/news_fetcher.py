"""
News Fetcher
Fetches and analyzes financial news from multiple sources
"""

import requests
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
import asyncio

# Local imports
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import config, logger

class NewsFetcher:
    """Fetches financial news from multiple sources"""
    
    def __init__(self):
        self.logger = logger
        self.config = config
        self.news_api_key = config.NEWS_API_KEY
        
        # RSS Feed URLs
        self.rss_feeds = {
            'economic_times': 'https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms',
            'moneycontrol': 'https://www.moneycontrol.com/rss/marketreports.xml',
            'business_standard': 'https://www.business-standard.com/rss/markets-106.rss',
            'reuters': 'https://feeds.reuters.com/reuters/businessNews'
        }
        
        # Keywords for market impact classification
        self.bullish_keywords = [
            'growth', 'profit', 'earnings beat', 'upgrade', 'buy rating',
            'positive', 'strong', 'recovery', 'expansion', 'investment'
        ]
        
        self.bearish_keywords = [
            'loss', 'decline', 'downgrade', 'sell rating', 'weak',
            'recession', 'inflation', 'crisis', 'cut', 'negative'
        ]
        
        self.logger.info("News Fetcher initialized")
    
    async def get_morning_news(self) -> List[Dict[str, Any]]:
        """Get morning news for market impact"""
        try:
            news_items = []
            
            # Get news from News API if available
            if self.news_api_key:
                api_news = await self._get_news_api_data('morning')
                news_items.extend(api_news)
            
            # Get news from RSS feeds
            rss_news = await self._get_rss_news()
            news_items.extend(rss_news[:3])  # Add top 3 RSS items
            
            # Sort by relevance and impact
            news_items = self._filter_and_rank_news(news_items, 'morning')
            
            return news_items[:5]  # Return top 5 news items
            
        except Exception as e:
            self.logger.error(f"Error fetching morning news: {str(e)}")
            return self._get_fallback_news('morning')
    
    async def get_evening_news(self) -> List[Dict[str, Any]]:
        """Get evening news for next day impact"""
        try:
            news_items = []
            
            # Get news from News API if available
            if self.news_api_key:
                api_news = await self._get_news_api_data('evening')
                news_items.extend(api_news)
            
            # Get news from RSS feeds
            rss_news = await self._get_rss_news()
            news_items.extend(rss_news[:3])
            
            # Filter for evening news (future impact)
            news_items = self._filter_and_rank_news(news_items, 'evening')
            
            return news_items[:5]
            
        except Exception as e:
            self.logger.error(f"Error fetching evening news: {str(e)}")
            return self._get_fallback_news('evening')
    
    async def _get_news_api_data(self, time_period: str) -> List[Dict[str, Any]]:
        """Get news from News API"""
        try:
            if not self.news_api_key:
                return []
            
            # Determine search terms based on time period
            if time_period == 'morning':
                query = 'indian stock market OR nifty OR sensex OR economy'
            else:
                query = 'stock market OR economic policy OR earnings OR federal reserve'
            
            url = 'https://newsapi.org/v2/everything'
            params = {
                'q': query,
                'apiKey': self.news_api_key,
                'language': 'en',
                'sortBy': 'publishedAt',
                'pageSize': 10,
                'from': (datetime.now() - timedelta(hours=12)).isoformat()
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            news_items = []
            
            for article in data.get('articles', []):
                if article.get('title') and article.get('description'):
                    news_item = {
                        'title': article['title'],
                        'summary': article['description'][:200] + '...' if len(article['description']) > 200 else article['description'],
                        'url': article['url'],
                        'source': article.get('source', {}).get('name', 'News API'),
                        'published_at': article['publishedAt'],
                        'impact': self._classify_impact(article['title'] + ' ' + article['description'])
                    }
                    news_items.append(news_item)
            
            return news_items
            
        except Exception as e:
            self.logger.error(f"Error fetching News API data: {str(e)}")
            return []
    
    async def _get_rss_news(self) -> List[Dict[str, Any]]:
        """Get news from RSS feeds"""
        news_items = []
        
        for feed_name, feed_url in self.rss_feeds.items():
            try:
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:3]:  # Get top 3 from each feed
                    # Clean and format the summary
                    summary = getattr(entry, 'summary', getattr(entry, 'description', ''))
                    if hasattr(BeautifulSoup, 'get_text'):
                        summary = BeautifulSoup(summary, 'html.parser').get_text()
                    
                    news_item = {
                        'title': entry.title,
                        'summary': summary[:200] + '...' if len(summary) > 200 else summary,
                        'url': entry.link,
                        'source': feed_name.replace('_', ' ').title(),
                        'published_at': getattr(entry, 'published', datetime.now().isoformat()),
                        'impact': self._classify_impact(str(entry.title) + ' ' + str(summary))
                    }
                    news_items.append(news_item)
                    
            except Exception as e:
                self.logger.error(f"Error fetching RSS feed {feed_name}: {str(e)}")
                continue
        
        return news_items
    
    def _classify_impact(self, text: str) -> str:
        """Classify news impact as bullish, bearish, or neutral"""
        text_lower = text.lower()
        
        bullish_score = sum(1 for keyword in self.bullish_keywords if keyword in text_lower)
        bearish_score = sum(1 for keyword in self.bearish_keywords if keyword in text_lower)
        
        if bullish_score > bearish_score:
            return 'Bullish'
        elif bearish_score > bullish_score:
            return 'Bearish'
        else:
            return 'Neutral'
    
    def _filter_and_rank_news(self, news_items: List[Dict], time_period: str) -> List[Dict[str, Any]]:
        """Filter and rank news by relevance and impact"""
        try:
            # Remove duplicates based on title similarity
            unique_news = []
            seen_titles = set()
            
            for item in news_items:
                title_words = set(item['title'].lower().split())
                is_duplicate = False
                
                for seen_title in seen_titles:
                    seen_words = set(seen_title.lower().split())
                    if len(title_words.intersection(seen_words)) >= len(title_words) * 0.6:
                        is_duplicate = True
                        break
                
                if not is_duplicate:
                    unique_news.append(item)
                    seen_titles.add(item['title'])
            
            # Sort by impact and recency
            def sort_key(item):
                impact_score = {'Bullish': 3, 'Bearish': 3, 'Neutral': 1}
                return impact_score.get(item.get('impact', 'Neutral'), 1)
            
            unique_news.sort(key=sort_key, reverse=True)
            
            return unique_news
            
        except Exception as e:
            self.logger.error(f"Error filtering news: {str(e)}")
            return news_items
    
    def _get_fallback_news(self, time_period: str) -> List[Dict[str, Any]]:
        """Get fallback news when APIs fail"""
        if time_period == 'morning':
            return [
                {
                    'title': 'Market Opening: Global Cues Mixed',
                    'summary': 'Indian markets expected to open with mixed global cues. Monitor key levels and sectoral movements.',
                    'url': '#',
                    'source': 'Trading Bot',
                    'impact': 'Neutral'
                },
                {
                    'title': 'Economic Data Release Today',
                    'summary': 'Important economic indicators scheduled for release. Watch for market volatility.',
                    'url': '#',
                    'source': 'Trading Bot',
                    'impact': 'Neutral'
                }
            ]
        else:
            return [
                {
                    'title': 'Market Close: Daily Summary',
                    'summary': 'Markets closed with mixed performance. Key events and earnings to watch tomorrow.',
                    'url': '#',
                    'source': 'Trading Bot',
                    'impact': 'Neutral'
                },
                {
                    'title': 'Overnight Global Developments',
                    'summary': 'Monitor overnight global market movements and policy announcements.',
                    'url': '#',
                    'source': 'Trading Bot',
                    'impact': 'Neutral'
                }
            ]
    
    def get_sector_news(self, sector: str) -> List[Dict[str, Any]]:
        """Get sector-specific news"""
        try:
            # This would be implemented with sector-specific queries
            # For now, return general market news
            return []
        except Exception as e:
            self.logger.error(f"Error fetching sector news: {str(e)}")
            return []
    
    def test_news_fetching(self) -> bool:
        """Test news fetching functionality"""
        try:
            # Test RSS feeds
            test_news = asyncio.run(self._get_rss_news())
            success = len(test_news) > 0
            
            if success:
                self.logger.info(f"News test successful: {len(test_news)} items fetched")
            else:
                self.logger.warning("News test: No items fetched")
            
            return success
            
        except Exception as e:
            self.logger.error(f"News test failed: {str(e)}")
            return False

# Test function
async def test_news_fetcher():
    """Test news fetcher functionality"""
    fetcher = NewsFetcher()
    
    print("Testing news fetcher...")
    
    # Test morning news
    morning_news = await fetcher.get_morning_news()
    print(f"Morning news items: {len(morning_news)}")
    
    if morning_news:
        print(f"Sample: {morning_news[0]['title']}")
        print(f"Impact: {morning_news[0]['impact']}")
    
    # Test connection
    success = fetcher.test_news_fetching()
    print(f"News fetcher test: {'✅ Success' if success else '❌ Failed'}")

if __name__ == "__main__":
    asyncio.run(test_news_fetcher())