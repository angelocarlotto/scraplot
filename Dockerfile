# Use Python 3.11 slim image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome and matching ChromeDriver
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV CHROME_BIN=/usr/bin/google-chrome-stable

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose port (Railway will set PORT env variable)
EXPOSE 8080

# Create start script that generates env config and starts only API server
# The API server will serve both API endpoints and static files
RUN echo '#!/bin/bash\n\
echo "Generating environment configuration..."\n\
python3 generate_env.py\n\
echo "Starting Flask server (API + Static files) on port ${PORT:-8080}..."\n\
python api.py\n\
' > /app/start.sh && chmod +x /app/start.sh

# Start the Flask server
CMD ["/app/start.sh"]
