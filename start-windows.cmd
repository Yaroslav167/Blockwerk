@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe py -3.12 -m venv .venv
if errorlevel 1 exit /b 1
if not exist .venv\.blockwerk-0.4.0-ready (
    .venv\Scripts\python.exe -m pip install -r requirements.txt
    if errorlevel 1 exit /b 1
    echo ready>.venv\.blockwerk-0.4.0-ready
)
.venv\Scripts\python.exe main.py %*
