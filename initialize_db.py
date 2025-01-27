import sqlite3
from pathlib import Path
from config import config

# To initialize the database manually run: python3 initialize_db.py
# Verify db using SQLite shell: sqlite3 db/ml_dashboard.db
# To show current tables: .tables
# To show db schema: .schema metrics
# To quit: .exit

# initialize_db.py
# run: python initialize_db.py
def initialize_db():
    Path(config.db_path.parent).mkdir(parents=True, exist_ok=True)
    
    with sqlite3.connect(config.db_path) as conn:
        cursor = conn.cursor()

        # Create tables with improved schema
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historical_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                date TEXT NOT NULL,
                open REAL NOT NULL,
                high REAL NOT NULL,
                low REAL NOT NULL,
                close REAL NOT NULL,
                volume INTEGER NOT NULL,
                UNIQUE(symbol, date)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                model_type TEXT NOT NULL,
                mse REAL NOT NULL,
                rmse REAL NOT NULL,
                mae REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                predictions TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        print("Database initialized successfully")

if __name__ == "__main__":
    initialize_db()
