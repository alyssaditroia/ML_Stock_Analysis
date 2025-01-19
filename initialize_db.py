import sqlite3

# To initialize the database manually run: python3 initialize_db.py
# Verify db using SQLite shell: sqlite3 db/ml_dashboard.db
# To show current tables: .tables
# To show db schema: .schema metrics
# To quit: .exit

DB_FILE = "db/ml_dashboard.db"  # Path to SQLite database file

def initialize_db():
    conn = sqlite3.connect(DB_FILE)  # Connect to the database (creates the file if it doesn't exist)
    cursor = conn.cursor()

    # Create `metrics` table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_type TEXT NOT NULL,
            period TEXT NOT NULL,
            rmse REAL,
            mae REAL,
            mse REAL,
            accuracy REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create historical_data table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historical_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            date TEXT,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INTEGER,
            UNIQUE(symbol, date)  -- Prevent duplicate entries for the same symbol and date
        )
    """)

    # Create `predictions` table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            period TEXT NOT NULL,
            predictions TEXT NOT NULL, -- JSON string of predictions
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    print("Database and tables created successfully.")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    initialize_db()
