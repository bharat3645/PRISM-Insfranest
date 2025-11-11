@echo off
echo ================================
echo   Starting InfraNest Backend
echo ================================
echo.

cd /d "%~dp0infranest\core"

echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.9+
    pause
    exit /b 1
)

echo.
echo Installing/Updating dependencies...
pip install -r requirements.txt --quiet

echo.
echo Starting backend server on http://localhost:8000
echo.
echo NOTE: Clean server using Groq AI only
echo Keep this window open while using the system
echo.
python server.py

pause

