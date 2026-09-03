# ==============================================================================
# ORION Headless & Web Server Container
# ==============================================================================
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (build essentials, ALSA audio, portaudio)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    portaudio19-dev \
    libasound2-dev \
    libsndfile1 \
    espeak \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies first for Docker caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Expose Web Dashboard & REST API
EXPOSE 8080

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV HEADLESS=true

# Launch FastAPI web dashboard & remote control node
CMD ["python", "api/server.py"]
