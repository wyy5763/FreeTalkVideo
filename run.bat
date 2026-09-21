@echo off
setlocal
cd /d %~dp0
echo ========================================
echo FreeTalkVideo - CPU mode
echo ========================================

if not exist .venv (
  echo [1/4] Creating Python 3.10 virtual environment...
  py -3.10 -m venv .venv
  if errorlevel 1 (
    echo Failed to create .venv. Please install Python 3.10 and ensure py -3.10 works.
    pause
    exit /b 1
  )
)
call .venv\Scripts\activate.bat
echo [2/4] Installing FreeTalkVideo dependencies...
python -m pip install -U pip
python -m pip install -r requirements.txt
if errorlevel 1 (
  echo Dependency installation failed.
  pause
  exit /b 1
)
if not exist .env (
  copy /Y .env.example .env >nul
  echo Created .env. Please edit paths if your G: drive layout is different.
)
echo [3/4] Checking Ollama...
where ollama >nul 2>nul
if errorlevel 1 (
  echo WARNING: Ollama was not found in PATH.
  echo Install Ollama, then run: ollama pull qwen3:4b
) else (
  ollama list
)
echo [4/4] Starting FreeTalkVideo...
python app.py
pause
