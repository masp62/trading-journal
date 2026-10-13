@echo off
REM Build frontend and start the complete application

REM Add Node.js to PATH (nvm installation)
set PATH=C:\Tools\nvm;C:\Tools\nvm\nodejs;%PATH%

echo Building frontend...
cd frontend
call npm install
call npm run build
cd ..

echo.
echo Starting FastAPI backend with integrated frontend...
call venv\Scripts\activate.bat
python run_api.py
