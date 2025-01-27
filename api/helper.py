
from datetime import datetime, timedelta
import yfinance as yf
from Stock_Analysis_ML.api.database import get_connection, get_latest_date, save_historical_data


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


def update_existing_data():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT symbol FROM historical_data")
    symbols = [row[0] for row in cursor.fetchall()]
    
    for symbol in symbols:
        latest_date = get_latest_date(symbol)
        if not latest_date:
            continue
            
        # Only fetch new data if last stored date is older than today
        if datetime.strptime(latest_date, "%Y-%m-%d").date() < datetime.today().date():
            stock = yf.Ticker(symbol)
            new_data = stock.history(
                start=latest_date,
                end=datetime.today().strftime("%Y-%m-%d"),
                interval="1d"
            ).dropna()
            
            if not new_data.empty:
                formatted_data = {
                    row.name.strftime("%Y-%m-%d"): {
                        "Open": row["Open"],
                        "High": row["High"],
                        "Low": row["Low"],
                        "Close": row["Close"],
                        "Volume": row["Volume"],
                    }
                    for _, row in new_data.iterrows()
                }
                save_historical_data(symbol, formatted_data)