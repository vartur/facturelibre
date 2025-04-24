# Use a slim official Python image
FROM python:3.13-slim

# Set environment variables early to ensure consistent behavior
ENV LANG=fr_FR.UTF-8 \
    LANGUAGE=fr_FR:fr \
    LC_ALL=fr_FR.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set port
ENV PORT=8000

# Install required system dependencies in one layer
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libffi-dev \
        libcairo2 \
        libpango-1.0-0 \
        libpangocairo-1.0-0 \
        libgdk-pixbuf2.0-0 \
        libglib2.0-0 \
        fonts-open-sans \
        locales \
        build-essential \
        curl \
    && sed -i 's/# fr_FR.UTF-8 UTF-8/fr_FR.UTF-8 UTF-8/' /etc/locale.gen \
    && locale-gen fr_FR.UTF-8 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Expose the port
EXPOSE ${PORT}

# Health check to ensure the application is running
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl --fail http://localhost:$PORT/health || exit 1

# Launch the server
CMD uvicorn main:app --host 0.0.0.0 --port $PORT


