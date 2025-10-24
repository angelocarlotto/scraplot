# Use Python 3.11 slim image
FROM python:3.11-slim

# Install system dependencies for Chrome and Selenium
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

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
