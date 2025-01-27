# api/ml/training.py
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.preprocessing import MinMaxScaler
from config import config
from datetime import datetime, timedelta

class StockModelTrainer:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.window_size = 60  # Days of historical data used for prediction
        
    def _create_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Create time-series features"""
        data = data.copy()
        data['day'] = (data.index - data.index.min()).days
        data['day_of_week'] = data.index.dayofweek
        data['month'] = data.index.month
        data['volume_pct_change'] = data['Volume'].pct_change()
        return data.dropna()

    def prepare_data(self, data: pd.DataFrame) -> tuple:
        """Prepare data for training"""
        data = self._create_features(data)
        features = data[['Open', 'High', 'Low', 'Volume', 'day', 'day_of_week', 'month', 'volume_pct_change']]
        target = data['Close']
        
        # Normalize features
        scaled_features = self.scaler.fit_transform(features)
        
        # Create sequences
        X, y = [], []
        for i in range(self.window_size, len(features)):
            X.append(scaled_features[i-self.window_size:i])
            y.append(target.iloc[i])
            
        return np.array(X), np.array(y)

    def train_model(self, data: pd.DataFrame) -> tuple:
        """Train and evaluate model"""
        X, y = self.prepare_data(data)
        train_size = int(len(X) * 0.8)
        
        X_train, X_test = X[:train_size], X[train_size:]
        y_train, y_test = y[:train_size], y[train_size:]
        
        model = RandomForestRegressor(
            n_estimators=200,
            max_depth=15,
            random_state=42,
            n_jobs=-1
        )
        
        model.fit(X_train, y_train)
        predictions = model.predict(X_test)
        
        metrics = {
            "mse": mean_squared_error(y_test, predictions),
            "rmse": np.sqrt(mean_squared_error(y_test, predictions)),
            "mae": mean_absolute_error(y_test, predictions),
            "model_type": "RandomForest"
        }
        
        return model, metrics

    def predict_future(self, model, data: pd.DataFrame, days: int) -> dict:
        """Generate future predictions"""
        latest_data = data.iloc[-self.window_size:].copy()
        predictions = {}
        
        for i in range(days):
            # Prepare input data
            features = self._create_features(latest_data)
            scaled_features = self.scaler.transform(features)
            X = scaled_features[-self.window_size:].reshape(1, -1)
            
            # Make prediction
            pred = model.predict(X)[0]
            date = latest_data.index[-1] + timedelta(days=1)
            
            # Create new row for recursive prediction
            new_row = latest_data.iloc[-1].copy()
            new_row.name = date
            new_row['Close'] = pred
            new_row['Open'] = pred * 0.99
            new_row['High'] = pred * 1.01
            new_row['Low'] = pred * 0.98
            new_row['Volume'] = latest_data['Volume'].mean()
            
            latest_data = pd.concat([latest_data, pd.DataFrame([new_row])])
            
            predictions[date.strftime("%Y-%m-%d")] = round(pred, 2)
            
        return predictions