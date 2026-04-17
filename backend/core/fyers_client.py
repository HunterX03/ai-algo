from fyers_apiv3.FyersModel import FyersModel
from fyers_apiv3.FyersWebsocket import data_ws
import os
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import asyncio

logger = logging.getLogger(__name__)

class FyersClient:
    def __init__(self):
        self.api_id = os.getenv('FYERS_API_ID', '')
        self.secret = os.getenv('FYERS_API_SECRET', '')
        self.access_token = os.getenv('FYERS_ACCESS_TOKEN', '')
        self.client = None
        self.ws = None
        
        if self.access_token:
            self.client = FyersModel(
                client_id=self.api_id,
                token=self.access_token,
                is_async=False,
                log_path=""
            )
        else:
            logger.warning("Fyers access token not configured")
    
    def get_quotes(self, symbols: List[str]) -> Dict:
        """Get real-time quotes for symbols"""
        if not self.client:
            return {'s': 'error', 'message': 'Client not initialized'}
        
        try:
            symbol_string = ",".join(symbols[:50])
            response = self.client.quotes({"symbols": symbol_string})
            return response
        except Exception as e:
            logger.error(f"Error fetching quotes: {e}")
            return {'s': 'error', 'message': str(e)}
    
    def get_historical(self, symbol: str, resolution: str = "D", days: int = 365) -> Dict:
        """Get historical OHLCV data"""
        if not self.client:
            return {'s': 'error', 'message': 'Client not initialized'}
        
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            data = {
                "symbol": symbol,
                "resolution": resolution,
                "date_format": "0",
                "range_from": int(start_date.timestamp()),
                "range_to": int(end_date.timestamp()),
                "cont_flag": "1"
            }
            
            response = self.client.history(data)
            return response
        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            return {'s': 'error', 'message': str(e)}
    
    def get_market_depth(self, symbol: str) -> Dict:
        """Get market depth for symbol"""
        if not self.client:
            return {'s': 'error', 'message': 'Client not initialized'}
        
        try:
            data = {"symbols": [symbol], "ohlcv_flag": "1"}
            response = self.client.market_depth(data)
            return response
        except Exception as e:
            logger.error(f"Error fetching market depth: {e}")
            return {'s': 'error', 'message': str(e)}
    
    def format_nse_symbol(self, symbol: str) -> str:
        """Format symbol for NSE"""
        if ':' in symbol:
            return symbol
        return f"NSE:{symbol}-EQ"

fyers_client = FyersClient()