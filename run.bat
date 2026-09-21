@echo off
setlocal
cd /d %~dp0

if not exist .venv (
  echo [1/3] Creating Python virtual environment...
  py -3.10 -m venv .venv
)

call .venv\Scripts\activate.bat

echo [2/3] Installing/refreshing Python dependencies...
python -m pip install -U pip
python -m pip install -r requirements.txt

if not exist .env (
  copy /Y .env.example .env >nul
  echo Created .env from .env.example. Please configure it before first generation.
)

echo [3/3] Starting FreeTalkVideo...
python app.py
pause
