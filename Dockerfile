FROM python:3.11-slim
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y ffmpeg libsndfile1 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy project files
COPY pyproject.toml /app/
COPY . /app

# Install build dependencies
RUN pip install --upgrade pip setuptools wheel

# Install project and dependencies
RUN pip install .

EXPOSE 8000 8001 8002 8003 8004 8005 8006 8501

CMD ["sleep", "infinity"]
