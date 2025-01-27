# api/routes/metrics.py
from fastapi import APIRouter, HTTPException
from api.database import DatabaseManager
from api.schemas import ModelMetrics
import matplotlib.pyplot as plt
import io
import base64

router = APIRouter(prefix="/api/py/metrics", tags=["metrics"])

@router.get("/{symbol}", response_model=list[ModelMetrics])
def get_metrics(symbol: str):
    try:
        with DatabaseManager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT symbol, model_type, mse, rmse, mae, created_at
                FROM metrics
                WHERE symbol = ?
                ORDER BY created_at DESC
            """, (symbol,))
            return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chart/{symbol}")
def get_metrics_chart(symbol: str):
    try:
        metrics = get_metrics(symbol)
        if not metrics:
            raise HTTPException(status_code=404, detail="No metrics found")
        
        dates = [m['created_at'] for m in metrics]
        rmse_values = [m['rmse'] for m in metrics]
        mae_values = [m['mae'] for m in metrics]

        plt.figure(figsize=(10, 6))
        plt.plot(dates, rmse_values, label='RMSE')
        plt.plot(dates, mae_values, label='MAE')
        plt.xlabel('Training Date')
        plt.ylabel('Error Value')
        plt.title(f'Model Performance Over Time - {symbol}')
        plt.legend()
        plt.xticks(rotation=45)
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        plt.close()
        
        return {"chart": base64.b64encode(buf.read()).decode('utf-8')}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))