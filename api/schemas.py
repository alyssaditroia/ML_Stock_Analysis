# api/schemas.py
from datetime import datetime
from pydantic import BaseModel

class StockData(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int

class PredictionResult(BaseModel):
    symbol: str
    predictions: dict
    last_updated: datetime

class ModelMetrics(BaseModel):
    symbol: str
    model_type: str
    mse: float
    rmse: float
    mae: float
    created_at: datetime