@echo off
REM Install Python dependencies

echo Creating virtual environment...
if not exist venv (
    python -m venv venv
)

echo Installing Python dependencies...
venv\Scripts\python.exe -m pip install -r requirements.txt

echo.
echo Installation complete!
echo.
echo To start the API server, run:
echo   start_api.bat
echo.
echo To use the CLI, run:
echo   python src/main.py
echo.
pause
