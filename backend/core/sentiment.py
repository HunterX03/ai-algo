import logging
import os
from typing import List, Dict
import requests
from datetime import datetime

logger = logging.getLogger(__name__)

# Lightweight keyword-based sentiment (no torch/transformers needed)
POSITIVE_KEYWORDS = [
    'upgrade', 'buy', 'bullish', 'profit', 'growth', 'outperform', 'beat',
    'strong', 'record', 'surge', 'rally', 'gain', 'positive', 'upbeat',
    'expand', 'dividend', 'acquisition', 'launch', 'breakthrough', 'revenue'
]
NEGATIVE_KEYWORDS = [
    'downgrade', 'sell', 'bearish', 'loss', 'decline', 'underperform', 'miss',
    'weak', 'drop', 'crash', 'fall', 'negative', 'concern', 'cut', 'layoff',
    'debt', 'default', 'investigation', 'fraud', 'warning', 'risk'
]


class SentimentAnalyzer:
    def __init__(self):
        self.serp_api_key = os.getenv('SERP_API_KEY', '')
        logger.info("Sentiment analyzer initialized (keyword-based, lightweight)")

    def analyze_text(self, text: str) -> Dict:
        if not text:
            return {'label': 'neutral', 'score': 0.0}
        text_lower = text.lower()
        pos = sum(1 for w in POSITIVE_KEYWORDS if w in text_lower)
        neg = sum(1 for w in NEGATIVE_KEYWORDS if w in text_lower)
        total = pos + neg
        if total == 0:
            return {'label': 'neutral', 'score': 0.0}
        score = (pos - neg) / total
        if score > 0.2:
            return {'label': 'positive', 'score': round(score, 3)}
        elif score < -0.2:
            return {'label': 'negative', 'score': round(score, 3)}
        return {'label': 'neutral', 'score': round(score, 3)}

    async def get_news_sentiment(self, ticker: str) -> Dict:
        try:
            news_items = await self._fetch_news(ticker)
            if not news_items:
                return {
                    'ticker': ticker, 'overall_sentiment': 0.0,
                    'sentiment_label': 'neutral', 'news_count': 0, 'headlines': []
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
            overall = sum(sentiments) / len(sentiments) if sentiments else 0.0
            label = 'positive' if overall > 0.2 else ('negative' if overall < -0.2 else 'neutral')
            return {
                'ticker': ticker, 'overall_sentiment': round(overall, 3),
                'sentiment_label': label, 'news_count': len(news_items),
                'headlines': analyzed_news, 'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting news sentiment: {e}")
            return {
                'ticker': ticker, 'overall_sentiment': 0.0,
                'sentiment_label': 'neutral', 'news_count': 0, 'headlines': []
            }

    async def _fetch_news(self, ticker: str) -> List[Dict]:
        if not self.serp_api_key or 'PUT_YOUR' in self.serp_api_key:
            return self._mock_news(ticker)
        try:
            url = "https://serpapi.com/search"
            params = {
                "engine": "google_news", "q": f"{ticker} stock NSE India",
                "api_key": self.serp_api_key, "num": 10
            }
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get('news_results', [])
            return self._mock_news(ticker)
        except Exception as e:
            logger.error(f"SERP API error: {e}")
            return self._mock_news(ticker)

    def _mock_news(self, ticker: str) -> List[Dict]:
        return [
            {'title': f'{ticker} reports strong quarterly results, revenue beats estimates',
             'snippet': 'Company posted better-than-expected profit growth driven by strong demand',
             'source': 'Economic Times', 'link': '#', 'date': datetime.now().isoformat()},
            {'title': f'Brokerages upgrade {ticker} with revised target price',
             'snippet': 'Multiple analysts raise target citing robust fundamentals and expansion plans',
             'source': 'Moneycontrol', 'link': '#', 'date': datetime.now().isoformat()},
            {'title': f'{ticker} announces expansion into new markets',
             'snippet': 'Strategic launch expected to drive revenue growth in coming quarters',
             'source': 'LiveMint', 'link': '#', 'date': datetime.now().isoformat()},
            {'title': f'FII buying continues in {ticker}, delivery percentage rises',
             'snippet': 'Institutional interest surges with delivery volumes hitting 3-month high',
             'source': 'Business Standard', 'link': '#', 'date': datetime.now().isoformat()},
            {'title': f'{ticker} sector faces headwinds amid global uncertainty',
             'snippet': 'Risk of decline as macro concerns weigh on sentiment',
             'source': 'NDTV Profit', 'link': '#', 'date': datetime.now().isoformat()},
        ]
