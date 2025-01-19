import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error
from typing import Tuple, Dict


class StockPredictor:

    def __init__(self, model_type: str = "Linear Regression"):
        if model_type == "Linear Regression":
            self.model = LinearRegression()
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
        self.model_type = model_type

    # Train the model
    def train(self, X_train: np.ndarray, y_train: np.ndarray):
        self.model.fit(X_train, y_train)

    # Make predictions using trained model
    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X)

    # Evaluate model using mse rmse mae
    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, float]:
        y_pred = self.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, y_pred)

        return {
            "mse": mse,
            "rmse": rmse,
            "mae": mae,
        }

    # Predict future stock prices for x amount of days
    def future_predictions(self, last_day: int, days: int) -> Dict[str, float]:
        if last_day is None or days <= 0:
            raise ValueError("Invalid input for future prediction.")

        future_days = np.arange(last_day + 1, last_day + 1 + days).reshape(-1, 1)
        predictions = self.predict(future_days)

        return {f"Day {i+1}": round(price, 2) for i, price in enumerate(predictions)}



    # Prepare data for training and testing
    @staticmethod
    def prepare_data(data) -> Tuple[np.ndarray, np.ndarray]:
        if not isinstance(data.index, pd.DatetimeIndex):
            raise ValueError("Data index must be of type DatetimeIndex.")

        if "Close" not in data.columns:
            raise ValueError("The data must contain a 'Close' column.")

        # Fill missing values
        data = data.ffill().bfill()

        data['Date'] = data.index
        data['Day'] = (data['Date'] - data['Date'].min()).dt.days
        X = data[['Day']].values
        y = data['Close'].values
        return X, y

