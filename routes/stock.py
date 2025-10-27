from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from utils.data_fetcher import StockDataFetcher
from models.b_stock_predictor import StockPredictor
import os

stock_bp = Blueprint('stock', __name__)

@stock_bp.route('/current/<ticker>', methods=['GET'])
@jwt_required()
def get_current_price(ticker):
    """Get current stock price"""
    data = StockDataFetcher.get_current_price(ticker.upper())
    
    if not data:
        return jsonify({'error': 'Stock not found'}), 404
    
    info = StockDataFetcher.get_stock_info(ticker.upper())
    
    return jsonify({
        'ticker': ticker.upper(),
        'price_data': data,
        'info': info
    }), 200

@stock_bp.route('/history/<ticker>', methods=['GET'])
@jwt_required()
def get_history(ticker):
    """Get historical stock data"""
    period = request.args.get('period', '1y')
    
    df = StockDataFetcher.get_stock_data(ticker.upper(), period)
    
    if df is None or df.empty:
        return jsonify({'error': 'No data found'}), 404
    
    # Convert to JSON format
    history = {
        'dates': df.index.strftime('%Y-%m-%d').tolist(),
        'close': df['Close'].tolist(),
        'open': df['Open'].tolist(),
        'high': df['High'].tolist(),
        'low': df['Low'].tolist(),
        'volume': df['Volume'].tolist()
    }
    
    return jsonify({
        'ticker': ticker.upper(),
        'history': history
    }), 200

@stock_bp.route('/predict/<ticker>', methods=['POST'])
@jwt_required()
def predict_stock(ticker):
    """Predict future stock prices"""
    data = request.get_json()
    days = data.get('days', 7)
    
    # Fetch historical data
    df = StockDataFetcher.get_stock_data(ticker.upper(), period='2y')
    
    if df is None or df.empty:
        return jsonify({'error': 'No data found'}), 404
    
    # Check if model exists
    model_path = f'saved_models/{ticker.upper()}_model.h5'
    predictor = StockPredictor(ticker.upper())
    
    # Train or load model
    if not os.path.exists(model_path):
        X, y = predictor.prepare_data(df)
        predictor.train(X, y, epochs=50)
        os.makedirs('saved_models', exist_ok=True)
        predictor.save_model(model_path)
    else:
        predictor.load_model(model_path)
        X, y = predictor.prepare_data(df)
        predictor.scaler.fit(df['Close'].values.reshape(-1, 1))
    
    # Make predictions
    predictions = predictor.predict_future(df, days=days)
    
    return jsonify({
        'ticker': ticker.upper(),
        'predictions': predictions.tolist(),
        'current_price': float(df['Close'].iloc[-1])
    }), 200
