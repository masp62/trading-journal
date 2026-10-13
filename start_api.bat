@echo off
REM Start the FastAPI server for Windows

cd /d "%~dp0"
call venv\Scripts\activate.bat
python run_api.py
