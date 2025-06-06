"""
Point d'entrée pour lancer l'application Flask PriceChecker
"""

from app import create_app

# Créer l'application
app = create_app()

if __name__ == '__main__':
    # L'initialisation de la DB se fait déjà dans create_app() avec le bon contexte
    print("🚀 Lancement de PriceChecker...")
    app.run(debug=True, host='0.0.0.0', port=5000)