# api/routes/stocks.py
from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
import pandas as pd
from api.database import DatabaseManager, ModelStore
from api.ml.training import StockModelTrainer
from api.schemas import StockData, PredictionResult
from config import config

router = APIRouter(prefix="/api/py/stock", tags=["stocks"])

@router.get("/{symbol}", response_model=dict[str, StockData])
def get_stock_data(symbol: str):
    try:
        data = DatabaseManager.fetch_historical_data(symbol)
        if not data:
            raise HTTPException(status_code=404, detail="No data found")
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/predict/{symbol}", response_model=PredictionResult)
def predict_stock_price(symbol: str, days: int = 7):
    try:
        # Load model and data
        model = ModelStore.load_model(symbol)
        data = DatabaseManager.fetch_historical_data(symbol)
        
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        if not data:
            raise HTTPException(status_code=404, detail="Data not found")
            
        # Prepare data
        df = pd.DataFrame.from_dict(data, orient='index')
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        
        # Generate predictions
        trainer = StockModelTrainer(symbol)
        predictions = trainer.predict_future(model, df, days)
        
        return {
            "symbol": symbol,
            "predictions": predictions,
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))