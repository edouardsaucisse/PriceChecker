@echo off
echo 📦 Installation de PriceCheck...
cd /d "%~dp0"

echo ✓ Création de l'environnement virtuel...
python -m venv venv

echo ✓ Activation de l'environnement...
call venv\Scripts\activate.bat

echo ✓ Installation des dépendances...
pip install -r requirements.txt

echo ✓ Initialisation de la base de données...
python database\models.py

echo 🎉 Installation terminée !
echo Pour démarrer l'application, exécutez start.bat
pause
