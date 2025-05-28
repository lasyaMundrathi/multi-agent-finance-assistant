from fastapi import FastAPI, UploadFile, File
import whisper, tempfile, os

app = FastAPI()
model = whisper.load_model("base")

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
