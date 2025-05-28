from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

app = FastAPI()

class AnalyzeRequest(BaseModel):
    data: List[Optional[Dict[str, Any]]]

@app.post("/analyze")
async def analyze(request: AnalyzeRequest):
    """
    Analyze market and filings data to assess risk, earnings, and sentiment.

    Returns a dictionary with:
    - 'risk_exposure': based on market change_pct (rounded to 2 decimal places)
    - 'earnings': combined filing headlines or a default message
    - 'sentiment': currently static as 'neutral'

    ::data[0]:: market info dict (expects 'change_pct')
    ::data[1]:: filings info dict (expects 'filings': List[str])
    """
    market, filings = (request.data + [None, None])[:2]

    change = market.get("change_pct") if market else None
    risk = f"{abs(round(change, 2))}%" if change is not None else "unknown"

    earnings = "; ".join(filings.get("filings", [])) if filings else "No filings found"

    return {
        "risk_exposure": risk,
        "earnings": earnings or "No filings found",
        "sentiment": "neutral"
    }
