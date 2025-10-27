import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
import os

class StockPredictor:
    """LSTM-based stock price prediction model"""
    
    def __init__(self, ticker):
        self.ticker = ticker
        self.model = None
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.look_back = 60  # Use 60 days to predict next day
    
    def prepare_data(self, df):
        """Prepare data for LSTM model"""
        # Use closing price for prediction
        data = df['Close'].values.reshape(-1, 1)
        
        # Scale data
        scaled_data = self.scaler.fit_transform(data)
        
        # Create sequences
        X, y = [], []
        for i in range(self.look_back, len(scaled_data)):
            X.append(scaled_data[i-self.look_back:i, 0])
            y.append(scaled_data[i, 0])
        
        X, y = np.array(X), np.array(y)
        X = np.reshape(X, (X.shape[0], X.shape[1], 1))
        
        return X, y
    
    def build_model(self):
        """Build LSTM neural network"""
        model = Sequential()
        
        # First LSTM layer
        model.add(LSTM(units=50, return_sequences=True, 
                       input_shape=(self.look_back, 1)))
        model.add(Dropout(0.2))
        
        # Second LSTM layer
        model.add(LSTM(units=50, return_sequences=True))
        model.add(Dropout(0.2))
        
        # Third LSTM layer
        model.add(LSTM(units=50))
        model.add(Dropout(0.2))
        
        # Output layer
        model.add(Dense(units=1))
        
        # Compile model
        model.compile(optimizer='adam', loss='mean_squared_error')
        
        self.model = model
        return model
    
    def train(self, X_train, y_train, epochs=50, batch_size=32):
        """Train the model"""
        if self.model is None:
            self.build_model()
        
        self.model.fit(X_train, y_train, epochs=epochs, 
                      batch_size=batch_size, verbose=1)
    
    def predict_future(self, df, days=7):
        """Predict future stock prices"""
        # Prepare last 60 days data
        data = df['Close'].values[-self.look_back:].reshape(-1, 1)
        scaled_data = self.scaler.transform(data)
        
        predictions = []
        current_batch = scaled_data.reshape(1, self.look_back, 1)
        
        for i in range(days):
            # Predict next day
            pred = self.model.predict(current_batch, verbose=0)[0]
            predictions.append(pred)
            
            # Update batch with prediction
            current_batch = np.append(current_batch[:, 1:, :], 
                                     [[pred]], axis=1)
        
        # Inverse transform predictions
        predictions = self.scaler.inverse_transform(predictions)
        
        return predictions.flatten()
    
    def save_model(self, filepath):
        """Save trained model"""
        if self.model:
            self.model.save(filepath)
    
    def load_model(self, filepath):
        """Load trained model"""
        if os.path.exists(filepath):
            self.model = load_model(filepath)
            return True
        return False
