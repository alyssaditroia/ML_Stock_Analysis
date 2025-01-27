# api/ml/validation.py
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error
from pathlib import Path
from datetime import datetime, timedelta
from Stock_Analysis_ML.api.ml.metrics import StockModelTrainer
from config import config

class ModelValidator:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.plot_dir = Path("plots")
        self.plot_dir.mkdir(exist_ok=True)

    def _create_plots(self, y_true, y_pred, title_suffix=""):
        plt.figure(figsize=(12, 6))
        plt.plot(y_true, label='Actual Price')
        plt.plot(y_pred, label='Predicted Price')
        plt.title(f"{self.symbol} Price Prediction {title_suffix}")
        plt.xlabel("Time")
        plt.ylabel("Price")
        plt.legend()
        plot_path = self.plot_dir / f"{self.symbol}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
        plt.savefig(plot_path)
        plt.close()
        return plot_path

    def walk_forward_validation(self, data: pd.DataFrame, window_size=200):
        test_metrics = []
        predictions = []
        actuals = []
        
        for i in range(window_size, len(data)):
            train = data.iloc[:i]
            test = data.iloc[i:i+1]
            
            # Train model
            trainer = StockModelTrainer(self.symbol)
            X_train, y_train = trainer.prepare_data(train)
            model = RandomForestRegressor(n_estimators=100, max_depth=10)
            model.fit(X_train, y_train)
            
            # Predict
            X_test, y_test = trainer.prepare_data(test)
            pred = model.predict(X_test)
            
            # Store results
            predictions.append(pred[0])
            actuals.append(y_test[0])
            test_metrics.append({
                'date': test.index[-1].strftime("%Y-%m-%d"),
                'actual': y_test[0],
                'predicted': pred[0],
                'error': y_test[0] - pred[0]
            })

        # Calculate final metrics
        mae = mean_absolute_error(actuals, predictions)
        rmse = np.sqrt(mean_squared_error(actuals, predictions))
        
        # Generate plot
        plot_path = self._create_plots(actuals, predictions, "Walk-Forward Validation")
        
        return {
            'mae': mae,
            'rmse': rmse,
            'plot_path': str(plot_path),
            'predictions': test_metrics
        }

    def backtest(self, data: pd.DataFrame, start_date: str):
        test_data = data[data.index >= pd.to_datetime(start_date)]
        if len(test_data) < 1:
            raise ValueError("No data available for backtesting period")
            
        X, y = StockModelTrainer(self.symbol).prepare_data(data)
        X_test, y_test = StockModelTrainer(self.symbol).prepare_data(test_data)
        
        model = ModelStore.load_model(self.symbol)
        predictions = model.predict(X_test)
        
        # Calculate metrics
        mae = mean_absolute_error(y_test, predictions)
        rmse = np.sqrt(mean_squared_error(y_test, predictions))
        
        # Generate plot
        plt.figure(figsize=(12, 6))
        plt.plot(test_data.index, y_test, label='Actual')
        plt.plot(test_data.index, predictions, label='Predicted')
        plt.title(f"{self.symbol} Backtest Results")
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.legend()
        plot_path = self.plot_dir / f"{self.symbol}_backtest_{start_date}.png"
        plt.savefig(plot_path)
        plt.close()
        
        return {
            'start_date': start_date,
            'end_date': data.index[-1].strftime("%Y-%m-%d"),
            'mae': mae,
            'rmse': rmse,
            'plot_path': str(plot_path)
        }

    def benchmark(self, data: pd.DataFrame):
        # Naive baseline: tomorrow's price = today's price
        baseline_preds = data['Close'].shift(1).dropna()
        actuals = data['Close'].iloc[1:]
        
        mae = mean_absolute_error(actuals, baseline_preds)
        rmse = np.sqrt(mean_squared_error(actuals, baseline_preds))
        
        # Generate comparison plot
        plt.figure(figsize=(12, 6))
        plt.plot(actuals.index, actuals, label='Actual')
        plt.plot(actuals.index, baseline_preds, label='Naive Baseline')
        plt.title(f"{self.symbol} Baseline Comparison")
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.legend()
        plot_path = self.plot_dir / f"{self.symbol}_baseline_comparison.png"
        plt.savefig(plot_path)
        plt.close()
        
        return {
            'baseline_mae': mae,
            'baseline_rmse': rmse,
            'plot_path': str(plot_path)
        }

    def plot_feature_importance(self, model, features):
        importances = model.feature_importances_
        indices = np.argsort(importances)[-10:]  # Top 10 features
        
        plt.figure(figsize=(10, 6))
        plt.title("Feature Importances")
        plt.barh(range(len(indices)), importances[indices], align='center')
        plt.yticks(range(len(indices)), [features[i] for i in indices])
        plt.xlabel("Relative Importance")
        plot_path = self.plot_dir / f"{self.symbol}_feature_importance.png"
        plt.savefig(plot_path)
        plt.close()
        return plot_path