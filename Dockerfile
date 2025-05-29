# Use slim base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system-level dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    ffmpeg \
    libespeak1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Optional: preload whisper model (change model size as needed)
RUN python3 -c "import whisper; whisper.load_model('small')"

# Copy app source code

COPY . .

# Expose relevant ports (if needed for FastAPI services)
EXPOSE 8000 8501

# Default command: can be overridden in docker-compose.yml
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
