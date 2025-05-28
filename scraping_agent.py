from fastapi import FastAPI, Query
import requests
from bs4 import BeautifulSoup

app = FastAPI()

@app.get("/filings")
def get_filings(ticker: str = Query("TSM", description="Company stock ticker symbol")):
    """
    Scrapes Yahoo Finance for news related to the given stock ticker.

    Args:
        ticker (str): Stock ticker symbol (e.g., AAPL, TSM)

    Returns:
        dict: {
            "ticker": str,
            "filings": List[str] – up to 3 long-enough news summaries
        }
    """
    url = f"https://finance.yahoo.com/quote/{ticker}/news"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        # Get all paragraph tags that seem long enough to be news summaries
        articles = [p.text.strip() for p in soup.find_all("p") if len(p.text.strip()) > 60]

        return {
            "ticker": ticker,
            "filings": articles[:3] or ["No filings or news found."]
        }

    except Exception as e:
        return {"error": f"Failed to fetch filings for {ticker}: {e}"}
