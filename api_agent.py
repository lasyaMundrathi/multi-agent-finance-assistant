from fastapi import FastAPI, Query
import yfinance as yf

app = FastAPI()

@app.get("/market-data")
def get_market_data(ticker: str = Query(..., description="Stock ticker like TSM or AAPL")):
    """
    Returns recent market data for the given stock ticker.

    Output includes:
    - 'latest_close': most recent closing price
    - 'change_pct': percentage change from previous close
    - 'volume': most recent trading volume

    ::ticker:: stock symbol (e.g., AAPL, TSM)
    """
    try:
        hist = yf.Ticker(ticker).history(period="2d")
        if hist.empty:
            return {"error": "No data found. Try a different ticker."}

        latest, previous = hist["Close"].iloc[-1], hist["Close"].iloc[-2]
        change_pct = ((latest - previous) / previous) * 100

        return {
            "ticker": ticker,
            "latest_close": round(latest, 2),
            "change_pct": round(change_pct, 2),
            "volume": int(hist["Volume"].iloc[-1])
        }
    except Exception as e:
        return {"error": str(e)}
