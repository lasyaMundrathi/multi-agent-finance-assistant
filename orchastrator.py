# orchestrator.py

from fastapi import FastAPI, UploadFile, File
import requests
import re

# Confidence threshold for retrieval fallback
CONF_THRESHOLD = 0.6

app = FastAPI()

COMPANY_TICKERS = {
    "APPLE": "AAPL", "TESLA": "TSLA", "MICROSOFT": "MSFT", "GOOGLE": "GOOGL",
    "META": "META", "NETFLIX": "NFLX", "AMAZON": "AMZN", "NVIDIA": "NVDA", "TSMC": "TSM"
}

def make_clarify(prompt: str):
    return {"clarify": True, "clarify_prompt": prompt}

def dynamic_ticker_lookup(name: str) -> str:
    try:
        r = requests.get(
            "https://query1.finance.yahoo.com/v1/finance/search",
            params={"q": name}, timeout=5
        )
        r.raise_for_status()
        for item in r.json().get("quotes", []):
            sym = item.get("symbol", "")
            if sym.isalpha() and len(sym) <= 5:
                return sym.upper()
    except:
        pass
    return None

def extract_ticker(text: str) -> str:
    upper = text.upper()
    for cname, ticker in COMPANY_TICKERS.items():
        if cname in upper:
            return ticker
    m = re.search(r"\$([A-Z]{1,5})\b", upper)
    if m:
        return m.group(1)
    m = re.search(r"price of ([A-Za-z&. ]+)", text, re.I)
    if m:
        return dynamic_ticker_lookup(m.group(1).strip())
    for phrase in re.findall(r"\b([A-Z][a-z]+(?: [A-Z][a-z]+)*)\b", text):
        cand = dynamic_ticker_lookup(phrase)
        if cand:
            return cand
    return None

def classify_intent(query: str) -> str:
    q = query.lower()
    if "stock price" in q or re.search(r"price of [a-z]", q):
        return "price"
    if any(k in q for k in ["filing", "sec", "news"]):
        return "filings"
    if any(k in q for k in ["historical", "last quarter", "past", "p/e", "ratio"]):
        return "historical"
    if any(k in q for k in ["risk exposure", "allocation", "portfolio"]):
        return "portfolio"
    return "qa"

def pipeline(payload: dict, urls: list) -> dict:
    try:
        for url in urls:
            r = requests.post(url, json=payload, timeout=20)
            r.raise_for_status()
            payload = r.json()
        return {"response": payload.get("text", "")}
    except Exception as e:
        return {"error": str(e)}

@app.post("/query")
async def handle_query(file: UploadFile = File(...)) -> dict:
    try:
        # 1) Transcribe
        stt = requests.post(
            "http://voice-agent:8001/stt",
            files={"file": file.file},
            timeout=15
        )
        stt.raise_for_status()
        text = stt.json().get("text", "").strip()

        # 2) Classify
        intent = classify_intent(text)

        # 3) PRICE
        if intent == "price":
            ticker = extract_ticker(text)
            if not ticker:
                return make_clarify("I couldn’t detect which stock you meant. Could you rephrase?")
            md = requests.get(f"http://api-agent:8002/market-data?ticker={ticker}", timeout=20).json()
            if "error" in md:
                return make_clarify(f"Error fetching data for {ticker}. Could you try another ticker?")
            return {"response": f"{ticker}: ${md['latest_close']:.2f}, {md['change_pct']:+.2f}%"}

        # 4) FILINGS
        if intent == "filings":
            ticker = extract_ticker(text)
            if not ticker:
                return make_clarify("I couldn’t detect which company’s filings you want. Could you rephrase?")
            filings = requests.get(f"http://scraping-agent:8003/filings?ticker={ticker}", timeout=20) \
                              .json().get("filings", [])
            if not filings:
                return make_clarify(f"No filings found for {ticker}. Could you clarify your request?")
            summary = "\n".join(f"- {f}" for f in filings[:3])
            return {"response": f"Latest for {ticker}:\n{summary}"}

        # 5) HISTORICAL / QA with fallback
        if intent in ["historical", "qa"]:
            rv = requests.post("http://retriever-agent:8004/retrieve", json={"query": text}, timeout=20)
            rv.raise_for_status()
            data = rv.json()
            conf = data.get("confidence", 0.0)
            results = data.get("results", [])

            if conf < CONF_THRESHOLD or not results:
                return make_clarify(
                    "I didn’t catch that confidently or couldn’t find relevant info. "
                    "Could you please rephrase or provide more detail?"
                )

            # reshape for analyze → generate
            analyze_payload = {"data": results}
            an = requests.post("http://analysis-agent:8005/analyze", json=analyze_payload, timeout=20)
            an.raise_for_status()
            gen = requests.post("http://language-agent:8006/generate", json=an.json(), timeout=20)
            gen.raise_for_status()
            return {"response": gen.json().get("text", "")}

        # 6) PORTFOLIO with generalized clarification
        if intent == "portfolio":
            allocs = requests.get("http://portfolio-agent:8007/portfolio-allocation", timeout=20).json()
            # If the service returns nothing or any None fields, clarify
            if not isinstance(allocs, dict) or any(v is None for v in allocs.values()):
                return make_clarify(
                    "I couldn’t determine your portfolio details. "
                    "Could you please rephrase or provide more detail on your portfolio?"
                )
            # proceed normally
            m = requests.get("http://api-agent:8002/market-data?ticker=TSMC", timeout=10).json()
            f = requests.get("http://scraping-agent:8003/filings", timeout=10).json()
            return pipeline({"data": [m, f]}, [
                "http://analysis-agent:8005/analyze", "http://language-agent:8006/generate"
            ])

        # 7) DEFAULT QA-only
        return pipeline({"query": text}, ["http://language-agent:8006/generate"])

    except Exception as e:
        return {"error": str(e)}
