from transformers import pipeline
import logging
import os
from typing import List, Dict
import requests
from datetime import datetime

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    def __init__(self):
        try:
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model="ProsusAI/finbert",
                tokenizer="ProsusAI/finbert"
            )
            logger.info("FinBERT sentiment analyzer loaded successfully")
        except Exception as e:
            logger.error(f"Error loading FinBERT: {e}")
            self.sentiment_pipeline = None
        
        self.serp_api_key = os.getenv('SERP_API_KEY', '')
    
    def analyze_text(self, text: str) -> Dict:
        """Analyze sentiment of text"""
        if not self.sentiment_pipeline or not text:
            return {'label': 'neutral', 'score': 0.5}
        
        try:
            result = self.sentiment_pipeline(text[:512])[0]
            sentiment_map = {
                'positive': {'label': 'positive', 'score': result['score']},
                'negative': {'label': 'negative', 'score': -result['score']},
                'neutral': {'label': 'neutral', 'score': 0.0}
            }
            return sentiment_map.get(result['label'].lower(), {'label': 'neutral', 'score': 0.0})
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return {'label': 'neutral', 'score': 0.0}
    
    async def get_news_sentiment(self, ticker: str) -> Dict:
        """Get news and sentiment for ticker"""
        try:
            news_items = await self._fetch_news(ticker)
            
            if not news_items:
                return {
                    'ticker': ticker,
                    'overall_sentiment': 0.0,
                    'sentiment_label': 'neutral',
                    'news_count': 0,
                    'headlines': []
                }
            
            sentiments = []
            analyzed_news = []
            
            for item in news_items[:10]:
                text = f"{item.get('title', '')} {item.get('snippet', '')}"
                sentiment = self.analyze_text(text)
                sentiments.append(sentiment['score'])
                
                analyzed_news.append({
                    'title': item.get('title', ''),
                    'source': item.get('source', 'Unknown'),
                    'link': item.get('link', ''),
                    'date': item.get('date', ''),
                    'sentiment': sentiment['label'],
                    'sentiment_score': sentiment['score']
                })
            
            overall_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.0
            
            if overall_sentiment > 0.2:
                sentiment_label = 'positive'
            elif overall_sentiment < -0.2:
                sentiment_label = 'negative'
            else:
                sentiment_label = 'neutral'
            
            return {
                'ticker': ticker,
                'overall_sentiment': float(overall_sentiment),
                'sentiment_label': sentiment_label,
                'news_count': len(news_items),
                'headlines': analyzed_news,
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error getting news sentiment: {e}")
            return {
                'ticker': ticker,
                'overall_sentiment': 0.0,
                'sentiment_label': 'neutral',
                'news_count': 0,
                'headlines': []
            }
    
    async def _fetch_news(self, ticker: str) -> List[Dict]:
        """Fetch news using SERP API"""
        if not self.serp_api_key or self.serp_api_key == 'PUT_YOUR_SERP_API_KEY_HERE':
            return self._mock_news(ticker)
        
        try:
            url = "https://serpapi.com/search"
            params = {
                "engine": "google_news",
                "q": f"{ticker} stock NSE India",
                "api_key": self.serp_api_key,
                "num": 10
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                news_results = data.get('news_results', [])
                return news_results
            else:
                return self._mock_news(ticker)
        
        except Exception as e:
            logger.error(f"Error fetching news from SERP API: {e}")
            return self._mock_news(ticker)
    
    def _mock_news(self, ticker: str) -> List[Dict]:
        """Mock news data when API not available"""
        return [
            {
                'title': f'{ticker} shows strong quarterly performance',
                'snippet': 'Company reports better than expected earnings',
                'source': 'Mock News',
                'link': '#',
                'date': datetime.now().isoformat()
            },
            {
                'title': f'Analysts upgrade {ticker} target price',
                'snippet': 'Positive outlook from major brokerages',
                'source': 'Mock News',
                'link': '#',
                'date': datetime.now().isoformat()
            }
        ]