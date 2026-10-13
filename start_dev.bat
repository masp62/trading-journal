@echo off
REM Start both backend and frontend in development mode

REM Add Node.js to PATH (nvm installation)
set PATH=C:\Tools\nvm;C:\Tools\nvm\nodejs;%PATH%

echo Starting backend API on port 8000...
start "Trading Journal API" cmd /k "call venv\Scripts\activate.bat && python run_api.py"

echo Waiting for backend to start...
timeout /t 3 /nobreak > nul

echo Starting frontend dev server on port 5173...
cd frontend
start "Trading Journal Frontend" cmd /k "set PATH=C:\Tools\nvm;C:\Tools\nvm\nodejs;%PATH% && npm run dev"

echo.
echo ========================================
echo Backend API: http://localhost:8000
echo Frontend:    http://localhost:5173
echo API Docs:    http://localhost:8000/docs
echo ========================================
