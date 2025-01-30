import pathlib

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db/ml_dashboard.db"
MODEL_STORE_PATH = BASE_DIR / "models"
TRAINING_PERIOD_DAYS = 3 * 365
DATA_CACHE_DAYS = 1

class Config:
    def __init__(self):
        self.db_path = DB_PATH
        self.model_store_path = MODEL_STORE_PATH
        self.training_period_days = TRAINING_PERIOD_DAYS
        self.data_cache_days = DATA_CACHE_DAYS

config = Config()