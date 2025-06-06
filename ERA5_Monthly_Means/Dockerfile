# Use an official Python runtime as the base image
FROM python:3.12-slim

# Set working directory in the container
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install SQLite (ensure it's available)
RUN apt-get update && apt-get install -y sqlite3 && rm -rf /var/lib/apt/lists/*

# Copy application files
COPY era5client.py .
COPY era5server.py .
COPY auth.env .
COPY south_asia_monthly_new.db .

# Command to run the application
CMD ["python", "era5client.py"]