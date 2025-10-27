import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

class StockDataFetcher:
    """Fetch stock data using yfinance API"""
    
    @staticmethod
    def get_stock_data(ticker, period='1y'):
        """
        Fetch historical stock data
        
        Args:
            ticker: Stock symbol (e.g., 'AAPL', 'GOOGL')
            period: Time period ('1d', '5d', '1mo', '3mo', '6mo', '1y', '5y')
        
        Returns:
            DataFrame with stock data
        """
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period=period)
            
            if df.empty:
                return None
            
            return df
        except Exception as e:
            print(f"Error fetching data for {ticker}: {str(e)}")
            return None
    
    @staticmethod
    def get_current_price(ticker):
        """Get current stock price"""
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period='1d')
            
            if data.empty:
                return None
            
            return {
                'price': data['Close'].iloc[-1],
                'open': data['Open'].iloc[-1],
                'high': data['High'].iloc[-1],
                'low': data['Low'].iloc[-1],
                'volume': data['Volume'].iloc[-1]
            }
        except Exception as e:
            print(f"Error: {str(e)}")
            return None
    
    @staticmethod
    def get_stock_info(ticker):
        """Get stock company information"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            return {
                'name': info.get('longName', ticker),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': info.get('marketCap', 0)
            }
        except Exception as e:
            print(f"Error: {str(e)}")
            return None
