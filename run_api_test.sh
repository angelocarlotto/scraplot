#!/bin/bash

# Start API and Test Script

echo "Starting Web Scraper API on port 5001..."
/Users/angelocarlotto/Desktop/github2/scraplot/.venv/bin/python /Users/angelocarlotto/Desktop/github2/scraplot/api.py &
API_PID=$!

echo "API started with PID: $API_PID"
echo "Waiting 5 seconds for API to initialize..."
sleep 5

echo ""
echo "Running test..."
echo "======================================================================"
/Users/angelocarlotto/Desktop/github2/scraplot/.venv/bin/python /Users/angelocarlotto/Desktop/github2/scraplot/quick_test.py

echo ""
echo "======================================================================"
echo "Stopping API server (PID: $API_PID)..."
kill $API_PID

echo "Done!"
