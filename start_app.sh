#!/bin/bash

echo "========================================================================"
echo "Starting Web Scraper Application"
echo "========================================================================"
echo ""

# Start the API server in the background
echo "1. Starting API server on http://localhost:5001..."
/Users/angelocarlotto/Desktop/github2/scraplot/.venv/bin/python /Users/angelocarlotto/Desktop/github2/scraplot/api.py &
API_PID=$!

echo "   API server started with PID: $API_PID"
echo ""

# Wait for API to start
echo "2. Waiting for API to initialize..."
sleep 3
echo ""

# Start a simple HTTP server for the React interface
echo "3. Starting web interface on http://localhost:8000..."
cd /Users/angelocarlotto/Desktop/github2/scraplot
python3 -m http.server 8000 &
WEB_PID=$!

echo "   Web server started with PID: $WEB_PID"
echo ""

echo "========================================================================"
echo "✅ Application is running!"
echo "========================================================================"
echo ""
echo "🌐 Open your browser and go to:"
echo "   http://localhost:8000"
echo ""
echo "📡 API Server:"
echo "   http://localhost:5001"
echo ""
echo "Press Ctrl+C to stop all servers..."
echo "========================================================================"
echo ""

# Wait for user to stop
trap "echo ''; echo 'Stopping servers...'; kill $API_PID $WEB_PID 2>/dev/null; echo 'Done!'; exit" INT

# Keep script running
wait
