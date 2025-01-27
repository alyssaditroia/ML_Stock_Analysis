from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import stocks, metrics
from config import config

app = FastAPI(
    title="Stock Analysis API",
    docs_url="/api/py/docs",
    openapi_url="/api/py/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stocks.router)
app.include_router(metrics.router)

@app.on_event("startup")
async def startup_event():
    # Initialize database and directories
    config.model_store_path.mkdir(exist_ok=True, parents=True)