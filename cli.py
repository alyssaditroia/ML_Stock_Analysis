import click
from datetime import datetime, timedelta
import yfinance as yf
from Stock_Analysis_ML.api.ml.validation import ModelValidator
from api.database import DatabaseManager, ModelStore
from api.ml.training import StockModelTrainer
from config import config
import pandas as pd

# run: python cli.py fetch-data VOO 
# python cli.py train-model VOO
# python cli.py validate-model VOO
# python cli.py backtest VOO
# python cli.py backtest VOO --start=2023-01-01
# python cli.py benchmark VOO
# python cli.py feat-im VOO

@click.group()
def cli():
    pass

@cli.command()
@click.argument('symbol', help="Enter Stock Ticker e.g. VOO\nUsage example: python cli.py validate-model VOO")
def validate_model(symbol: str):
    """Run walk-forward validation on the model"""
    db = DatabaseManager()
    data = db.fetch_historical_data(symbol)
    df = pd.DataFrame.from_dict(data, orient='index')
    df.index = pd.to_datetime(df.index)
    
    validator = ModelValidator(symbol)
    results = validator.walk_forward_validation(df)
    
    click.echo(f"Walk-Forward Validation Results for {symbol}:")
    click.echo(f"MAE: {results['mae']:.2f}")
    click.echo(f"RMSE: {results['rmse']:.2f}")
    click.echo(f"Plot saved to: {results['plot_path']}")

@cli.command()
@click.argument('symbol')
@click.option('--start', default='2023-01-01', help='Start date for backtest\nFormat: yyyy-mm-dd')
def backtest(symbol: str, start: str):
    """Backtest the model from specific start date"""
    db = DatabaseManager()
    data = db.fetch_historical_data(symbol)
    df = pd.DataFrame.from_dict(data, orient='index')
    df.index = pd.to_datetime(df.index)
    
    validator = ModelValidator(symbol)
    results = validator.backtest(df, start)
    
    click.echo(f"Backtest Results for {symbol} from {start}:")
    click.echo(f"MAE: {results['mae']:.2f}")
    click.echo(f"RMSE: {results['rmse']:.2f}")
    click.echo(f"Plot saved to: {results['plot_path']}")

@cli.command()
@click.argument('symbol')
def benchmark(symbol: str):
    """Compare model against naive baseline"""
    db = DatabaseManager()
    data = db.fetch_historical_data(symbol)
    df = pd.DataFrame.from_dict(data, orient='index')
    df.index = pd.to_datetime(df.index)
    
    validator = ModelValidator(symbol)
    results = validator.benchmark(df)
    
    click.echo(f"Baseline Comparison for {symbol}:")
    click.echo(f"Naive Baseline MAE: {results['baseline_mae']:.2f}")
    click.echo(f"Naive Baseline RMSE: {results['baseline_rmse']:.2f}")
    click.echo(f"Comparison plot saved to: {results['plot_path']}")

@cli.command()
@click.argument('symbol')
def feat_im(symbol: str):
    """Plot feature importance for trained model"""
    db = DatabaseManager()
    data = db.fetch_historical_data(symbol)
    df = pd.DataFrame.from_dict(data, orient='index')
    df.index = pd.to_datetime(df.index)
    
    model = ModelStore.load_model(symbol)
    trainer = StockModelTrainer(symbol)
    X, _ = trainer.prepare_data(df)
    
    features = df.drop(columns=['Close']).columns.tolist()
    validator = ModelValidator(symbol)
    plot_path = validator.plot_feature_importance(model, features)
    
    click.echo(f"Feature importance plot saved to: {plot_path}")

    
@cli.command()
@click.argument('symbol')
def fetch_data(symbol: str):
    """Fetch and update historical data for a stock symbol"""
    db = DatabaseManager()
    latest_date = db.get_latest_date(symbol)
    
    if latest_date:
        start_date = latest_date + timedelta(days=1)
        if start_date > datetime.now():
            click.echo(f"Data for {symbol} is already up-to-date.")
            return
    else:
        start_date = datetime.now() - timedelta(days=config.training_period_days)
    
    end_date = datetime.now()
    
    click.echo(f"Fetching data for {symbol} from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    stock = yf.Ticker(symbol)
    data = stock.history(
        start=start_date.strftime("%Y-%m-%d"),
        end=end_date.strftime("%Y-%m-%d"),
        interval="1d"
    ).dropna()
    
    if data.empty:
        click.echo(f"No data found for {symbol}")
        return
    
    formatted_data = {
        row.name.strftime("%Y-%m-%d"): {
            "Open": row["Open"],
            "High": row["High"],
            "Low": row["Low"],
            "Close": row["Close"],
            "Volume": row["Volume"],
        }
        for _, row in data.iterrows()
    }
    
    DatabaseManager.save_historical_data(symbol, formatted_data)
    click.echo(f"Successfully updated {len(formatted_data)} days of data for {symbol}")

@cli.command()
@click.argument('symbol')
def train_model(symbol: str):
    """Train and save a new model for the given symbol"""
    db = DatabaseManager()
    data = db.fetch_historical_data(symbol)
    
    if not data or len(data) < 100:
        click.echo(f"Insufficient data for {symbol}")
        return
    
    df = pd.DataFrame.from_dict(data, orient='index')
    df.index = pd.to_datetime(df.index)
    
    trainer = StockModelTrainer(symbol)
    model, metrics = trainer.train_model(df)
    
    DatabaseManager.save_model_metrics(symbol, metrics)
    ModelStore.save_model(symbol, model)
    
    click.echo(f"Model trained for {symbol} with metrics:")
    click.echo(f"MSE: {metrics['mse']:.2f}")
    click.echo(f"RMSE: {metrics['rmse']:.2f}")
    click.echo(f"MAE: {metrics['mae']:.2f}")

if __name__ == "__main__":
    cli()