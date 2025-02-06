# Use the official Python image as the base
FROM python:3.12-slim

# Install system dependencies required by WeasyPrint
RUN apt-get update && apt-get install -y \
    libffi-dev \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libglib2.0-0 \
    fonts-open-sans \
    locales \
    && rm -rf /var/lib/apt/lists/*

# Generate and set French locale
RUN sed -i 's/# fr_FR.UTF-8 UTF-8/fr_FR.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen fr_FR.UTF-8

# Set environment variables to use French locale
ENV LANG=fr_FR.UTF-8
ENV LANGUAGE=fr_FR:fr
ENV LC_ALL=fr_FR.UTF-8

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install -U pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

CMD ["python", "main.py", "invoice_data.json"]