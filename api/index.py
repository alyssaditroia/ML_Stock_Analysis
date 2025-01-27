from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from datetime import datetime, timedelta
from api.models import StockPredictor
from Stock_Analysis_ML.api.database import get_connection
from api.database import fetch_historical_data, get_latest_date, insert_metrics, fetch_metrics, save_historical_data
from initialize_db import initialize_db
from datetime import datetime, timedelta
# export PYTHONPATH=$PYTHONPATH:/Users/alyssaditroia/Desktop/Stock_Analysis/Stock_Analysis_ML
TRAINING_PERIOD_DAYS = 3 * 365
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


# Test: curl -v http://0.0.0.0:8000/api/py/stock/VOO
# Getting stock data
@app.get("/api/py/stock/{symbol}")
def get_stock_data(symbol: str):
    try:
        # Check existing data
        latest_date = get_latest_date(symbol)
        
        if latest_date:
            # Return existing data
            return fetch_historical_data(symbol, "", "")
            
        # Fetch initial 3 years of data if none exists
        end_date = datetime.today()
        start_date = end_date - timedelta(days=TRAINING_PERIOD_DAYS)
        
        stock = yf.Ticker(symbol)
        data = stock.history(
            start=start_date.strftime("%Y-%m-%d"),
            end=end_date.strftime("%Y-%m-%d")
        ).dropna()
        
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
def predict_stock_price(symbol: str, days: int = 7):
    try:
        # Get all historical data from DB
        historical_data = fetch_historical_data(symbol, "", "")
        
        if not historical_data or len(historical_data) < 250:
            raise HTTPException(status_code=404, detail="Insufficient historical data")
            
        # Convert to pandas DataFrame
        dates = list(historical_data.keys())
        data = pd.DataFrame({
            'Open': [v['Open'] for v in historical_data.values()],
            'High': [v['High'] for v in historical_data.values()],
            'Low': [v['Low'] for v in historical_data.values()],
            'Close': [v['Close'] for v in historical_data.values()],
            'Volume': [v['Volume'] for v in historical_data.values()],
        }, index=pd.to_datetime(dates))
        
        # Check for existing model
        predictor = StockPredictor.load_model(symbol)
        is_new_model = False
        
        if not predictor:
            # Train new model if none exists
            X, y = StockPredictor.prepare_data(data)
            predictor = StockPredictor(model_type="Linear Regression")
            predictor.train(X, y)
            predictor.save_model(symbol)
            is_new_model = True
            
        # Generate predictions
        last_day = data.index[-1].to_pydatetime()
        future_predictions = predictor.future_predictions(last_day, days)
        
        return {
            "symbol": symbol,
            "is_new_model": is_new_model,
            "predictions": future_predictions,
            "last_trained": predictor.last_trained if not is_new_model else datetime.now().isoformat(),
            "data_points": len(data)
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