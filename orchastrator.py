from fastapi import FastAPI, UploadFile, File
import requests, re

app = FastAPI()

COMPANY_TICKERS = {
    "APPLE": "AAPL", "TESLA": "TSLA", "MICROSOFT": "MSFT", "GOOGLE": "GOOGL",
    "META": "META", "NETFLIX": "NFLX", "AMAZON": "AMZN", "NVIDIA": "NVDA", "TSMC": "TSM"
}

def dynamic_ticker_lookup(name):
    """Search Yahoo Finance for a valid stock ticker matching the company name."""
    try:
        r = requests.get("https://query1.finance.yahoo.com/v1/finance/search", params={"q": name}, timeout=5)
        for item in r.json().get("quotes", []):
            s = item.get("symbol", "")
            if s.isalpha() and len(s) <= 5:
                return s.upper()
    except: pass

def extract_ticker(text):
    """Extract a stock ticker from the input text using rules, hints, or dynamic lookup."""
    u = text.upper()
    if t := next((t for n, t in COMPANY_TICKERS.items() if n in u), None): return t
    if m := re.search(r"\$([A-Z]{1,5})\b", u): return m.group(1)
    if m := re.search(r"price of ([A-Za-z&. ]+)", text, re.I): return dynamic_ticker_lookup(m.group(1).strip())
    for p in re.findall(r"\b([A-Z][a-z]+(?: [A-Z][a-z]+)*)\b", text):
        if t := dynamic_ticker_lookup(p): return t

def classify_intent(t):
    """Classify the user's query based on keyword patterns."""
    t = t.lower()
    if "stock price" in t or re.search(r"price of [a-z]+", t): return "price"
    if any(k in t for k in ["filing", "sec", "news"]): return "filings"
    if any(k in t for k in ["historical", "last quarter", "past", "p/e", "ratio"]): return "historical"
    if any(k in t for k in ["risk exposure", "allocation", "portfolio"]): return "portfolio"
    return "qa"

def pipeline(payload, urls):
    """Chain a sequence of services (e.g., retrieve → analyze → generate)."""
    try:
        for url in urls:
            r = requests.post(url, json=payload, timeout=20); r.raise_for_status()
            payload = r.json()
        return {"response": payload.get("text")} if payload.get("text") else {"error": "No output"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/query")
async def handle_query(file: UploadFile = File(...)):
    """
    Accepts a voice file, transcribes it, detects user intent,
    and routes the query to the appropriate microservice pipeline.
    """
    try:
        q = requests.post("http://localhost:8001/stt", files={"file": file.file}, timeout=15).json().get("text", "")
        print("🗣", q)

        intent = classify_intent(q)
        print("🏷", intent)

        if intent == "price":
            if not (t := extract_ticker(q)):
                return {"error": "Couldn’t detect the stock."}
            r = requests.get(f"http://localhost:8002/market-data?ticker={t}", timeout=10).json()
            return {"error": r["error"]} if "error" in r else {
                "response": f"{t}: ${r['latest_close']:.2f}, {r['change_pct']:+.2f}% from previous close."
            }

        if intent == "filings":
            if not (t := extract_ticker(q)):
                return {"error": "Couldn’t detect the company."}
            r = requests.get(f"http://localhost:8003/filings?ticker={t}", timeout=10).json().get("filings", [])
            return {"response": f"No news for {t}."} if not r else {
                "response": f"Latest for {t}:\n" + "\n".join(f"- {d}" for d in r[:3])
            }

        if intent == "historical":
            return pipeline({"query": q}, [
                "http://localhost:8004/retrieve",
                "http://localhost:8005/analyze",
                "http://localhost:8006/generate"
            ])

        if intent == "portfolio":
            m = requests.get("http://localhost:8002/market-data?ticker=TSMC", timeout=10).json()
            f = requests.get("http://localhost:8003/filings", timeout=10).json()
            return pipeline({"data": [m, f]}, [
                "http://localhost:8005/analyze",
                "http://localhost:8006/generate"
            ])

        return pipeline({"query": q}, [
            "http://localhost:8004/retrieve",
            "http://localhost:8006/generate"
        ])

    except Exception as e:
        return {"error": str(e)}
