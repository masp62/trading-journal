#!/bin/bash
# Start both backend and frontend in development mode

echo "Starting backend API on port 8000..."
source venv/bin/activate
python run_api.py &
BACKEND_PID=$!

echo "Waiting for backend to start..."
sleep 3

echo "Starting frontend dev server on port 5173..."
cd frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "========================================"
echo "Backend API: http://localhost:8000"
echo "Frontend:    http://localhost:5173"
echo "API Docs:    http://localhost:8000/docs"
echo "========================================"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
