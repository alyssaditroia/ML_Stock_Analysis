<p align="center">
  <a href="https://github.com/alyssaditroia/ML_Stock_Analysis">
    <img src="https://assets.vercel.com/image/upload/v1588805858/repositories/vercel/logo.png" height="40">
    <h3 align="center">Predictive Stock Analysis</h3>
  </a>
</p>

<p align="center">A web application for predictive stock analysis and historical data visualization using <a href="https://fastapi.tiangolo.com/">FastAPI</a> and <a href="https://nextjs.org/">Next.js</a>.</p>

<br/>

## Introduction

This is a hybrid application that combines the power of **Next.js 14** and **FastAPI** to deliver a seamless stock analysis experience. The application integrates predictive stock analysis using machine learning models, interactive charting for historical data, and model evaluation metrics.

## How It Works

The **FastAPI** backend is mapped into the **Next.js** app under `/api/py/`.

This is achieved using [`next.config.js` rewrites](https://nextjs.org/docs/pages/api-reference/next-config-js/rewrites) to route requests made to `/api/py/:path*` to the FastAPI server running in the `/api` directory.

Locally, the FastAPI server runs on `127.0.0.1:8000`, and the Next.js app interacts seamlessly with it for stock data retrieval, predictions, and database operations.

In production, the FastAPI backend can be hosted as [serverless Python functions](https://vercel.com/docs/concepts/functions/serverless-functions/runtimes/python) on Vercel.


## Developing Locally

Clone the repository with the following command:

```bash
git clone https://github.com/alyssaditroia/ML_Stock_Analysis.git
cd ML_Stock_Analysis

```
Create the Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```
Install Backend Dependencies

``` bash
pip install -r requirements.txt
```

Initialize SQLite Database

``` bash
python3 initialize_db.py
```

Start FastAPI Server

```bash
uvicorn api.index:app --host 0.0.0.0 --port 8000 --reload
```

