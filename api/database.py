import sqlite3
import json
from typing import List, Dict, Any

DB_FILE = "db/ml_dashboard.db"  # Path to your SQLite database file


# Connect to the database
def get_connection():
    return sqlite3.connect(DB_FILE)

# Insert metrics
def insert_metrics(model_type: str, period: str, rmse: float, mae: float, mse: float, accuracy: float):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO metrics (model_type, period, rmse, mae, mse, accuracy)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (model_type, period, rmse, mae, mse, accuracy))

    conn.commit()
    conn.close()


# Insert predictions
def insert_predictions(symbol: str, period: str, predictions: Dict[str, float]):
    conn = get_connection()
    cursor = conn.cursor()

    predictions_json = json.dumps(predictions)  # Convert predictions to JSON
    cursor.execute("""
        INSERT INTO predictions (symbol, period, predictions)
        VALUES (?, ?, ?)
    """, (symbol, period, predictions_json))

    conn.commit()
    conn.close()

# Save historical data
def save_historical_data(symbol: str, data: Dict[str, Dict[str, float]]):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    for date, values in data.items():
        cursor.execute("""
            INSERT OR IGNORE INTO historical_data (symbol, date, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (symbol, date, values["Open"], values["High"], values["Low"], values["Close"], values["Volume"]))

    conn.commit()
    conn.close()

# Fetch metrics
def fetch_metrics() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT model_type, period, rmse, mae, mse, accuracy, created_at FROM metrics")
    rows = cursor.fetchall()

    conn.close()

    # Convert rows into a list of dictionaries
    return [
        {
            "model_type": row[0],
            "period": row[1],
            "rmse": row[2],
            "mae": row[3],
            "mse": row[4],
            "accuracy": row[5],
            "created_at": row[6],
        }
        for row in rows
    ]

# Get historical data from db
def fetch_historical_data(symbol: str, start_date: str, end_date: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT date, open, high, low, close, volume
        FROM historical_data
        WHERE symbol = ? AND date BETWEEN ? AND ?
        ORDER BY date ASC
    """, (symbol, start_date, end_date))

    rows = cursor.fetchall()
    conn.close()

    # Convert to dictionary format
    return {
        row[0]: {
            "Open": row[1],
            "High": row[2],
            "Low": row[3],
            "Close": row[4],
            "Volume": row[5],
        }
        for row in rows
    }

# Fetch predictions by symbol
def fetch_predictions(symbol: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT symbol, period, predictions, created_at
        FROM predictions
        WHERE symbol = ?
    """, (symbol,))

    rows = cursor.fetchall()
    conn.close()

    # Convert rows into a list of dictionaries
    return [
        {
            "symbol": row[0],
            "period": row[1],
            "predictions": json.loads(row[2]),  # Convert JSON string back to dictionary
            "created_at": row[3],
        }
        for row in rows
    ]
