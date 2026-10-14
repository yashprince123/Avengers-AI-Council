@echo off
title Avengers AI Council Setup

echo.
echo ==========================================
echo       AVENGERS AI COUNCIL - SETUP
echo ==========================================
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo Python was not found in PATH.
    echo Install Python 3.11 or newer, then run this again.
    pause
    exit /b 1
)

echo Creating Python virtual environment...
python -m venv .venv

echo Installing Python dependencies...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo Pulling Qwen3.8 27B Q3_K_M through Ollama...
ollama pull smtek/Qwen3.8-27B:Q3_K_M

echo.
echo ==========================================
echo Setup complete.
echo Double-click run.bat to summon the council.
echo ==========================================
pause
