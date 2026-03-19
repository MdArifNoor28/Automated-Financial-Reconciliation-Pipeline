@echo off
title Financial Reconciliation Pipeline
echo 🚀 Starting Automated Scan...

:: 1. Move into your project folder
cd /d "%~dp0"

:: 2. Activate your 'Soundproof Room' (Virtual Environment)
call venv\Scripts\activate

:: 3. Run the Python Engine
python main.py

:: 4. Keep the window open so you can see the success rate
echo.
echo ✅ Scan Complete. Press any key to close this window.
pause