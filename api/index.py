from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from datetime import datetime, timedelta
from api.models import StockPredictor
from api.database import insert_metrics, fetch_metrics, save_historical_data
from initialize_db import initialize_db
# export PYTHONPATH=$PYTHONPATH:/Users/alyssaditroia/Desktop/Stock_Analysis/Stock_Analysis_ML

# Run: uvicorn index:app --host 0.0.0.0 --port 8000 --reload
app = FastAPI(docs_url="/api/py/docs", openapi_url="/api/py/openapi.json")

# Replace "*" with specific origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the database when the app starts
async def app_lifespan(app):
    initialize_db()
    yield

def get_date_range(period: str):
    end_date = datetime.today()
    if period.endswith('d'):
        days = int(period[:-1])
        start_date = end_date - timedelta(days=days)
    elif period.endswith('mo'):
        months = int(period[:-2])
        start_date = end_date - timedelta(weeks=4*months)
    elif period.endswith('y'):
        years = int(period[:-1])
        start_date = end_date - timedelta(days=365*years)
    else:
        start_date = end_date - timedelta(days=365*2)  # Default to 2 years
    return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")

# Test: curl -v http://0.0.0.0:8000/api/py/stock/VOO
# Getting stock data
@app.get("/api/py/stock/{symbol}")
def get_stock_data(symbol: str, period: str = "1mo"):
    try:
        # Try to get existing data first
        start_date, end_date = get_date_range(period)
        db_data = fetch_historical_data(symbol, start_date, end_date)
        
        if db_data:
            return db_data
            
        # If not found, fetch from yfinance
        stock = yf.Ticker(symbol)
        data = stock.history(period=period).dropna()
        if data.empty:
            raise HTTPException(status_code=404, detail="Stock data not found")

        formatted_data = {
            row.name.strftime("%Y-%m-%d"): {
                "Open": row["Open"],
                "High": row["High"],
                "Low": row["Low"],
                "Close": row["Close"],
                "Volume": row["Volume"],
            }
            for _, row in data.iterrows()
        }
        save_historical_data(symbol, formatted_data)
        return formatted_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

# Predicting stock prices
@app.get("/api/py/stock/predict/{symbol}")
def predict_stock_price(symbol: str, days: int = 7, period: str = "3mo"):
    if days <= 0:
        raise HTTPException(status_code=400, detail="Days parameter must be greater than 0.")

    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period=period).dropna()  # Drop missing values
        if data.empty:
            raise HTTPException(status_code=404, detail="Stock data not found")

        # Prepare data
        X, y = StockPredictor.prepare_data(data)

        # Train-test split
        train_size = int(len(X) * 0.8)
        X_train, X_test = X[:train_size], X[train_size:]
        y_train, y_test = y[:train_size], y[train_size:]

        # Initialize and train the model
        predictor = StockPredictor(model_type="Linear Regression")
        predictor.train(X_train, y_train)

        # Evaluate the model
        metrics = predictor.evaluate(X_test, y_test)

        # Save metrics to the database
        insert_metrics(
            model_type=predictor.model_type,
            period=period,
            rmse=round(metrics["rmse"], 2),
            mae=round(metrics["mae"], 2),
            mse=round(metrics["mse"], 2),
            accuracy=None  # Add accuracy if available
        )

        # Make future predictions
        last_day = X[-1][0]
        future_predictions = predictor.future_predictions(last_day, days)

        # Response
        return {
            "symbol": symbol,
            "model": predictor.model_type,
            "period": period,
            "metrics": metrics,
            "predictions": future_predictions,
            "is_new_model": True,  # Set this flag when new model is trained
            "training_data": {
                "actual": y_test.tolist(),
                "predicted": y_pred.tolist(),
                "dates": data.index[train_size:].strftime("%Y-%m-%d").tolist()
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@app.get("/api/py/model/metrics")
def get_model_metrics():
    try:
        metrics = fetch_metrics()  # Fetch metrics using your database function
        if not metrics:
            raise HTTPException(status_code=404, detail="No metrics found")
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))