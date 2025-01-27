import json
from contextlib import contextmanager
from datetime import datetime
import sqlite3
from typing import Dict, List, Optional
from config import config
import joblib

@contextmanager
def get_connection():
    conn = sqlite3.connect(config.db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

class DatabaseManager:
    @staticmethod
    def get_latest_date(symbol: str) -> Optional[datetime]:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT MAX(date) 
                FROM historical_data 
                WHERE symbol = ?
            """, (symbol,))
            result = cursor.fetchone()[0]
            return datetime.strptime(result, "%Y-%m-%d") if result else None

    @staticmethod
    def save_historical_data(symbol: str, data: Dict[str, Dict[str, float]]):
        with get_connection() as conn:
            cursor = conn.cursor()
            for date, values in data.items():
                cursor.execute("""
                    INSERT OR IGNORE INTO historical_data 
                    (symbol, date, open, high, low, close, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (symbol, date, 
                      values["Open"], values["High"], 
                      values["Low"], values["Close"], values["Volume"]))
            conn.commit()

    @staticmethod
    def fetch_historical_data(symbol: str) -> Dict[str, Dict[str, float]]:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT date, open, high, low, close, volume
                FROM historical_data
                WHERE symbol = ?
                ORDER BY date ASC
            """, (symbol,))
            return {
                row["date"]: {
                    "Open": row["open"],
                    "High": row["high"],
                    "Low": row["low"],
                    "Close": row["close"],
                    "Volume": row["volume"],
                }
                for row in cursor.fetchall()
            }

    @staticmethod
    def save_model_metrics(symbol: str, metrics: Dict):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO metrics 
                (symbol, model_type, mse, rmse, mae, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (symbol, metrics.get("model_type"), 
                  metrics["mse"], metrics["rmse"], 
                  metrics["mae"], datetime.now()))
            conn.commit()


class ModelStore:
    @staticmethod
    def save_model(symbol: str, model):
        config.model_store_path.mkdir(exist_ok=True)
        joblib.dump(model, config.model_store_path / f"{symbol}.joblib")

    @staticmethod
    def load_model(symbol: str):
        model_path = config.model_store_path / f"{symbol}.joblib"
        return joblib.load(model_path) if model_path.exists() else None
