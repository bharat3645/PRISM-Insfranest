@echo off
echo ================================
echo   Starting InfraNest Frontend
echo ================================
echo.

cd /d "%~dp0infranest"

echo Checking Node.js installation...
node --version
if errorlevel 1 (
    echo ERROR: Node.js not found! Please install Node.js 18+
    pause
    exit /b 1
)

echo.
echo Installing/Updating dependencies (this may take a minute)...
if not exist "node_modules" (
    call npm install
) else (
    echo Dependencies already installed.
)

echo.
echo Starting frontend server on http://localhost:5173
echo.
npm run dev

pause

