### Updated FastAPI Voice Agent Service (`voice_agent.py`)
from fastapi import FastAPI, UploadFile, File, Response
from pydantic import BaseModel
import whisper, tempfile, os
import pyttsx3

app = FastAPI()
model = whisper.load_model("base")

class TTSRequest(BaseModel):
    text: str

@app.post("/stt")
async def transcribe(file: UploadFile = File(...)):
    """Transcribes speech from an uploaded audio file using Whisper."""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(await file.read())
            path = tmp.name

        result = model.transcribe(path)
        os.remove(path)
        return {"text": result["text"]}
    except Exception as e:
        return {"error": f"Transcription failed: {e}"}

@app.post("/tts")
async def synthesize(request: TTSRequest):
    """Synthesizes speech from text using pyttsx3 and returns audio bytes."""
    try:
        engine = pyttsx3.init()
        # Save to temp WAV (pyttsx3 generates WAV)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            engine.save_to_file(request.text, tmp.name)
            engine.runAndWait()
            audio_path = tmp.name

        # Read WAV and return
        with open(audio_path, "rb") as f:
            data = f.read()
        os.remove(audio_path)
        return Response(content=data, media_type="audio/wav")
    except Exception as e:
        return {"error": f"TTS failed: {e}"}

### Simplified Client Wrapper (`agents/voice_agent.py`)

# agents/voice_agent.py
import requests, tempfile, os, wave
from types import SimpleNamespace

class VoiceAgent:
    """Client wrapper for STT and TTS microservices, no live recording."""
    def __init__(self, base_url="http://voice-agent:8001"):
        self.stt_url = f"{base_url}/stt"
        self.tts_url = f"{base_url}/tts"

    def speak(self, text: str):
        """Call the TTS service and play the resulting audio."""
        r = requests.post(self.tts_url, json={"text": text}, stream=True, timeout=10)
        r.raise_for_status()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            for chunk in r.iter_content(chunk_size=1024):
                tmp.write(chunk)
            path = tmp.name
        # Play using ffplay; ensure ffmpeg is installed
        os.system(f"ffplay -nodisp -autoexit {path} > /dev/null 2>&1")
        os.remove(path)

    def listen_from_file(self, file_path: str) -> SimpleNamespace:
        """Send an existing WAV file to STT and return transcription."""
        with open(file_path, "rb") as f:
            r = requests.post(self.stt_url, files={"file": f}, timeout=15)
        r.raise_for_status()
        data = r.json()
        return SimpleNamespace(text=data.get("text", ""))


