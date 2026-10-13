#!/bin/bash
# Build frontend and start the complete application

echo "Building frontend..."
cd frontend
npm install
npm run build
cd ..

echo ""
echo "Starting FastAPI backend with integrated frontend..."
source venv/bin/activate
python run_api.py
