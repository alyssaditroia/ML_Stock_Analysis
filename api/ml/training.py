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
        self.window_size = 30

    def _create_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Create time-series features"""
        data = data.copy()
        data['day'] = (data.index - data.index.min()).days
        data['day_of_week'] = data.index.dayofweek
        data['month'] = data.index.month
        data['volume_pct_change'] = data['Volume'].pct_change().fillna(0)
        return data.dropna(subset=['Close'])

    def prepare_data(self, data: pd.DataFrame, test_size=0.2) -> tuple:
        """Prepare data with temporal split"""
        data = self._create_features(data)

        # Temporal split
        split_idx = int(len(data) * (1 - test_size))
        train = data.iloc[:split_idx]
        test = data.iloc[split_idx:]

        # Prepare features
        X_train, y_train = self._transform_data(train, fit_scaler=True)
        X_test, y_test = self._transform_data(test, fit_scaler=False)
        #FIX should only return either or depending on what I am doing 
        return X_train, X_test, y_train, y_test

    def _transform_data(self, data: pd.DataFrame, fit_scaler=True):
        """Transform features for sklearn"""
        features = data.drop(columns=['Close'])
        target = data['Close']
        if fit_scaler:
            self.scaler.fit(features)
        scaled_features = self.scaler.transform(features)
        return scaled_features, target.values

    def train_model(self, data: pd.DataFrame) -> tuple:
        """Train and evaluate model with training and test data"""
        X_train, X_test, y_train, y_test = self.prepare_data(data)

        if len(X_train) < 100:
            raise ValueError("Insufficient data for training after preprocessing")

        model = RandomForestRegressor(
            n_estimators=150,
            max_depth=12,
            random_state=42,
            n_jobs=-1
        )
        model.fit(X_train, y_train)

        # Evaluate on training data
        train_predictions = model.predict(X_train)
        train_metrics = {
            "mse": mean_squared_error(y_train, train_predictions),
            "rmse": np.sqrt(mean_squared_error(y_train, train_predictions)),
            "mae": mean_absolute_error(y_train, train_predictions),
        }

        # Evaluate on test data
        test_predictions = model.predict(X_test)
        test_metrics = {
            "mse": mean_squared_error(y_test, test_predictions),
            "rmse": np.sqrt(mean_squared_error(y_test, test_predictions)),
            "mae": mean_absolute_error(y_test, test_predictions),
        }

        metrics = {
            "train": train_metrics,
            "test": test_metrics,
            "model_type": "RandomForest"
        }

        return model, metrics

    def predict_future(self, model, data: pd.DataFrame, days: int) -> dict:
        """Generate future predictions"""
        predictions = {}
        current_data = data.copy()
        
        for _ in range(days):
            # Prepare features for prediction
            features = self._create_features(current_data)
            features = features.iloc[-1:].drop(columns=['Close'], errors='ignore')
            
            # Generate prediction
            scaled_features = self.scaler.transform(features)
            pred = model.predict(scaled_features)[0]
            
            # Create new date
            last_date = current_data.index[-1]
            new_date = last_date + timedelta(days=1)
            
            # Create new row with predicted values
            new_row = {
                'Open': pred * 0.995,
                'High': pred * 1.01,
                'Low': pred * 0.99,
                'Close': pred,
                'Volume': current_data['Volume'].iloc[-7:].mean()
            }
            
            # Update data for recursive prediction
            current_data = current_data.append(pd.DataFrame([new_row], index=[new_date]))
            predictions[new_date.strftime("%Y-%m-%d")] = round(pred, 2)
            
        return predictions