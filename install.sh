#!/bin/bash
# Install Python dependencies

echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python -m venv venv
fi

echo "Installing Python dependencies..."
venv/bin/python -m pip install -r requirements.txt

echo ""
echo "Installation complete!"
echo ""
echo "To start the API server, run:"
echo "  ./start_api.sh"
echo ""
echo "To use the CLI, run:"
echo "  python src/main.py"
echo ""
