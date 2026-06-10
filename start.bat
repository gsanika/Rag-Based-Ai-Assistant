@echo off
title iPundit AI Assistant
color 0A

echo.
echo ==========================================
echo   iPundit AI Document Assistant
echo ==========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Install from https://python.org
    pause
    exit /b 1
)

REM Install dependencies
echo [1/3] Installing dependencies...
pip install -r requirements.txt --quiet

REM Start Ollama if installed
where ollama >nul 2>&1
if not errorlevel 1 (
    echo [2/3] Starting Ollama...
    start /B ollama serve
    timeout /t 3 /nobreak >nul
) else (
    echo [2/3] Ollama not found - will use fallback mode.
    echo       For AI answers: https://ollama.ai ^| then: ollama pull llama3
)

REM Launch app
echo [3/3] Launching iPundit AI Assistant...
echo.
echo  Open your browser at: http://localhost:8501
echo  Press Ctrl+C to stop.
echo.
streamlit run app/main.py --server.port=8501 --server.headless=false

pause
