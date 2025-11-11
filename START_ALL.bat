@echo off
echo ================================
echo   Starting InfraNest Full Stack
echo ================================
echo.

echo Starting backend server...
start "InfraNest Backend" cmd /k "cd /d %~dp0 && START_BACKEND.bat"

timeout /t 3 /nobreak >nul

echo Starting frontend server...
start "InfraNest Frontend" cmd /k "cd /d %~dp0 && START_FRONTEND.bat"

echo.
echo ================================
echo   Both servers are starting!
echo ================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Two windows will open - keep them open.
echo.
echo Opening browser...
timeout /t 5 /nobreak >nul
start http://localhost:5173
echo.
echo Press any key to close this window...
pause >nul

