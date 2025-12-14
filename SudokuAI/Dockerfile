# =========================
# Base Image
# =========================
FROM python:3.11-slim

# =========================
# Install system dependencies
# =========================
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        tesseract-ocr \
        libtesseract-dev \
        git \
        build-essential \
        pkg-config \
        && rm -rf /var/lib/apt/lists/*

# =========================
# Set working directory
# =========================
WORKDIR /app

# =========================
# Copy your app code
# =========================
COPY . /app

# =========================
# Install Python dependencies
# =========================
RUN pip install --no-cache-dir -r requirements.txt

# =========================
# Set Tesseract path (Linux)
# =========================
ENV TESSERACT_CMD=/usr/bin/tesseract

# =========================
# Run the app
# =========================
# Using CMD with Python to allow interactive input
CMD ["python", "main.py"]