# Universal Data Scanner - Dockerfile
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY ui/ ./ui/

# Create database directory
RUN mkdir -p backend

# Expose port
EXPOSE 8000

# Default command - run the FastAPI server
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
