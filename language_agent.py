from fastapi import FastAPI, Request
import json

app = FastAPI()

@app.post("/generate")
async def generate(req: Request):
    """
    Converts structured summary data into a natural language brief.

    Expects a JSON body with:
    - 'summary': dict or JSON string containing:
        - 'risk_exposure': str
        - 'earnings': str
        - 'sentiment': str

    Returns a dict with:
    - 'text': formatted verbal report
    """
    try:
        body = await req.json()
        summary = body.get("summary", {})

        # Parse JSON string if summary is passed as a string
        if isinstance(summary, str):
            try:
                summary = json.loads(summary)
            except json.JSONDecodeError:
                summary = {}

        risk = summary.get("risk_exposure", "unknown")
        earnings = summary.get("earnings", "")
        sentiment = summary.get("sentiment", "")

        text = (
            f"Today, your Asia tech allocation is {risk}."
            + (f" {earnings}." if earnings else "")
            + (f" Regional sentiment is {sentiment}." if sentiment else "")
        ).strip()

        return {"text": text}

    except Exception as e:
        return {"error": f"Language agent error: {e}"}
