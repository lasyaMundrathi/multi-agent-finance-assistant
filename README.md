# 🧠 Multi-Agent Finance Assistant

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.x-orange.svg)](https://streamlit.io/)  
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?logo=docker&logoColor=white)](https://www.docker.com/)

A voice-enabled financial analysis system that delivers real-time market briefs through orchestrated AI agents and supports interactive "clarify"-on-error flows via re-uploaded audio. Built with FastAPI, Streamlit, and RAG capabilities.

## 🚀 Demo
watch demo👇🏻✨
[![Watch Demo](demo.png)](https://www.youtube.com/watch?v=skZHYClgcSU)

---

## ✨ Key Features

### 🎙️ Voice Interface
Upload a WAV file → Whisper STT → orchestrator → AI agents → text answer

### 🔄 Clarification Flow
If any step (intent parsing, ticker extraction, data lookup, or RAG retrieval) fails or returns low-confidence, the system returns:

```json
{
  "clarify": true,
  "clarify_prompt": "Could you please rephrase or provide more detail?"
}
```

The Streamlit UI prompts you to re-upload a clearer/rephrased WAV.

### 📊 Real-Time Data
Live stock prices, earnings, and filings via dedicated micro-services.

### 🔍 RAG-Powered Retrieval
Pinecone/FAISS backed "retrieve → analyze → generate" pipeline with confidence-based fallback.

### 🛠️ Configurable Thresholds
`CONF_THRESHOLD` in `orchestrator.py` (default 0.6) controls when clarification is triggered.

### 📱 Web Dashboard
Streamlit UI guides you through upload, response, and clarification steps.

---

## 🏗️ Architecture

| Step | Service / Agent | Stack |
|------|----------------|-------|
| 1. STT | Whisper → FastAPI | whisper, FastAPI |
| 2. Intent classification | Orchestrator.py | Python, Regex |
| 3. Data lookup | API & Scraping Agents | yfinance, BeautifulSoup |
| 4. Retrieval (RAG) | Pinecone/FAISS | Pinecone SDK, FAISS |
| 5. Analysis | Analysis Agent | Pandas, NumPy |
| 6. Generation | Language Agent | OpenAI GPT-4 |
| 7. Clarification | Orchestrator fallback | JSON flag + Streamlit UI |

### Flow Diagram
```
Audio → STT → Intent → Data/RAG → Analysis → Generation → Response
               ↓                    ↓
            Clarify (if needed) ←──┘
```


## 🚀 Quick Start

### 1. Clone & Setup
```bash
git clone https://github.com/lasyaMundrathi/multi-agent-finance-assistant.git
cd multi-agent-finance-assistant
python -m venv venv && source venv/bin/activate  # on Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment
Copy and edit the environment file:

```bash
# OPENAI_API_KEY=your_key
# PINECONE_API_KEY=your_key
```

### 3. Run

#### Option A: Docker (Recommended)
```bash
docker-compose up --build
```

#### Option B: Local
```bash
uvicorn orchestrator:app --reload         # FastAPI orchestrator on :8000
uvicorn voice_service:app --port 8001      # STT/TTS service on :8001
# Start other agents on their configured ports...
streamlit run streamlit_app.py             # UI on :8501
```

### 4. Access
- **Web UI**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs


## 📡 API Endpoints

```bash
POST /query         (multipart WAV)    → { response }  or  { clarify, clarify_prompt }
POST /stt           (multipart WAV)    → { text }
GET  /market-data   (?ticker=XYZ)      → { latest_close, change_pct }
POST /retrieve      { query }          → { results: [...], confidence }
POST /analyze       { data: [...] }    → { data: [...] }
POST /generate      { data: [...] }    → { text }
GET  /portfolio-allocation → { asia_tech, ... }
```


## 💡 Usage Examples

### Voice Queries
- "What is the current stock price of Apple?"
- "Show me the latest SEC filings for Netflix."
- "What was Microsoft's P/E ratio last quarter?"
- "How much of my portfolio is allocated to Asia tech?"
- "Give me a summary of Tesla's historical performance."

### Clarification Flow
If you upload an ambiguous or noisy WAV, you'll see:

> 🔄 **Clarification needed:**  
> "I couldn't determine which stock you meant. Could you please rephrase?"

Then simply re-upload a clearer/rephrased audio.


## 📄 Implementation Notes

### Fallback Behavior
If any micro-service (intent, RAG, portfolio) fails or returns low confidence, orchestrator returns a JSON "clarify" flag (instead of server-side TTS) per the uploaded PDF spec.

### Streamlit UI
Catches `{ clarify: true }`, shows the `clarify_prompt`, and drives re-upload UI.


## 🤝 Contributing

1. Fork the repo
2. Create a feature branch (`git checkout -b feature-name`)
3. Make and test changes
4. Submit a pull request


## 🙏 Acknowledgments

- OpenAI for Whisper and GPT-4
- Pinecone for vector database services
- FastAPI and Streamlit teams for excellent frameworks
