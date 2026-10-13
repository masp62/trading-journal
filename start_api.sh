#!/bin/bash
# Start the FastAPI server

cd "$(dirname "$0")"
source venv/bin/activate
python run_api.py
