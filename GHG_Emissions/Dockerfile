# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything else (source code, db files, .env)
COPY . .

# Default to running the client (which launches the server internally via stdio)
CMD ["python", "EDGARclient.py"]
