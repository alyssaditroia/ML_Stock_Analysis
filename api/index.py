from fastapi import FastAPI, HTTPException
import yfinance as yf

# Run: uvicorn index:app --host 0.0.0.0 --port 8000 --reload
app = FastAPI(docs_url="/api/py/docs", openapi_url="/api/py/openapi.json")

# Test: curl -v http://0.0.0.0:8000/api/py/stock/VOO
@app.get("/api/py/stock/{symbol}")
def get_stock_data(symbol: str):
    stock = yf.Ticker(symbol)
    data = stock.history(period="1mo")
    if data.empty:
        raise HTTPException(status_code=404, detail="Stock data not found")
    return data.to_dict()