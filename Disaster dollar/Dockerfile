# Use official Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy all files to the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install spaCy model
RUN python -m spacy download en_core_web_sm

# Make start.sh executable
RUN chmod +x start.sh

# Expose port (if needed by your server)
EXPOSE 5000

# Run the shell script to start server & client
CMD ["./start.sh"]
