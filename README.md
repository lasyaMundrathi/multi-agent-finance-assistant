# 🧠 Finance Assistant – Voice-Driven Financial Analyst

An intelligent voice-enabled assistant that understands natural language queries, analyzes financial data, retrieves relevant market context, and responds conversationally — powered by modern AI tools like Whisper, LangChain, OpenAI, and Pinecone.

---

## 🗂 Project Structure

```
finance-assistant/
├── orchestrator.py         # Central router handling transcription → intent → pipeline
├── stt_agent.py           # Converts speech to text using Whisper
├── api_agent.py           # Retrieves current market data from yfinance
├── filings_agent.py       # Scrapes Yahoo Finance for latest news/filings
├── retrieve_agent.py      # Embeds + retrieves relevant finance documents from Pinecone
├── analysis_agent.py      # Analyzes structured market/filings data for risk & earnings
├── language_agent.py      # Converts structured summary to natural language brief
├── requirements.txt       # All Python dependencies
├── .env                   # Environment variables for keys (Pinecone, OpenAI)
└── README.md             # This file
```

---

## 🧱 System Architecture

> 📌 **Insert this image as `docs/architecture.png`**

![Architecture Diagram](docs/architecture.png)

### 🔁 Workflow

1. **Audio In** → Whisper transcribes to text  
2. **Intent Classification** → Determines what the query is asking  
3. **Pipeline Routing** → Routes to the correct agents (e.g., stock price, news, analysis)  
4. **Retrieval/Analysis** → Gets data from APIs or vector DB  
5. **Language Agent** → Converts analysis into a brief, spoken-style response  
6. **Result Out** → Returned as plain text, ready to be spoken or displayed  

---

## 📡 API Endpoints Overview

### `/query` — 🔄 Main voice-based query entrypoint
- **Accepts:** `audio/wav` file  
- **Returns:** Natural language response

### `/stt` — 🎙 Speech-to-text
- **Accepts:** `audio/wav` file  
- **Returns:**  
  ```json
  { "text": "transcribed text" }
  ```

### `/market-data` — 📈 Real-time stock data
- **Query param:** `?ticker=AAPL`
- **Returns:** Current price, % change, volume

### `/filings` — 📰 Latest filings/news
- **Query param:** `?ticker=TSLA`
- **Returns:** Top 3 long-form news snippets

### `/retrieve` — 🧠 Vector search from Pinecone
- **Body:**
  ```json
  { "query": "Apple earnings" }
  ```
- **Returns:** Top 3 related documents from finance corpus

### `/analyze` — 📊 Risk & earnings analyzer
- **Body:**
  ```json
  { "data": [market_dict, filings_dict] }
  ```
- **Returns:** Risk level, headline summary

### `/generate` — 💬 Language generation
- **Body:**
  ```json
  { "summary": { ... } }
  ```
- **Returns:**
  ```json
  { "text": "Today, your Asia tech allocation is moderate..." }
  ```

---

## 🧪 Demo

🎥 Insert a GIF or video demo here

---

## 🛠 Setup & Installation

### 1. Clone & Set Up Virtual Env
```bash
git clone https://github.com/yourname/multi-agent-finance-assistant.git
cd multi-agent-finance-assistant

python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows
.\.venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Create a .env File
```dotenv
OPENAI_API_KEY=your_openai_key_here
PINECONE_API_KEY=your_pinecone_key_here
```

### 3. Run the App
```bash
# Start all services via Docker Compose (requires Docker Desktop)
docker-compose up --build
```
Open your browser at http://localhost:8501 and upload a WAV query.

---

## ❓ FAQ

**Q: Can it support other languages?**  
A: Currently English only — but Whisper can be extended for multilingual support.

**Q: Can it give me historical trends or P/E ratios?**  
A: Yes — use queries like "Tesla's historical performance" or "Apple P/E ratio last quarter."

**Q: What kind of data does it retrieve?**  
A: Live stock prices (via yfinance), recent filings (Yahoo), vector-matched finance docs (Pinecone), and custom summaries.

**Q: Can I plug this into a chatbot or voice assistant?**  
A: Absolutely — integrate via web UIs, Streamlit dashboards, or voice platforms like Alexa.

---

## 💡 Future Ideas

- Support multilingual queries (Whisper + translation)
- Push-to-talk web UI using Streamlit or React
- More sophisticated sentiment/risk detection
- Portfolio tracking with personalized alerts

---

## 📬 Contributing & Questions

Open an issue or submit a pull request! Let's build smarter financial tools together.