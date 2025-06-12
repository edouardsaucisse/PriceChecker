@echo off
echo 🚀 Démarrage de PriceCheck...
cd /d "%~dp0"
call venv\Scripts\activate.bat
python run.py
pause
