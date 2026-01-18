@echo off
REM RSI Scalping Strategy - Backtest Runner
REM This batch file runs the main.py script with proper environment setup

echo ============================================================
echo RSI Scalping Strategy - Backtest Runner
echo ============================================================
echo.

REM Check if virtual environment exists
if exist ".venv\Scripts\python.exe" (
    echo [INFO] Using virtual environment...
    echo.
    REM Activate virtual environment and run script
    call .venv\Scripts\activate.bat
    python main.py
) else (
    echo [INFO] Virtual environment not found. Using system Python...
    echo [WARNING] Make sure all dependencies are installed!
    echo.
    python main.py
)

echo.
echo ============================================================
echo Backtest execution completed!
echo ============================================================
echo.
echo Press any key to exit...
pause >nul
