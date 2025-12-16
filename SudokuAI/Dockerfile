# Use official Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install Tesseract OCR
RUN apt-get update && \
    apt-get install -y tesseract-ocr libtesseract-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first (caches install if unchanged)
COPY SudokuAI/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY SudokuAI/ .

# Expose port for FastAPI
EXPOSE 8000

# Start uvicorn

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

