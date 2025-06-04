"""
Point d'entrée pour lancer l'application Flask PriceChecker
"""

from app import create_app
from database.models import init_db

# Créer l'application
app = create_app()

if __name__ == '__main__':
    # Initialiser la base de données si nécessaire
    print("🔧 Vérification de la base de données...")
    init_db()
    
    # Lancer l'application
    print("🚀 Lancement de PriceChecker...")
    app.run(debug=True, host='0.0.0.0', port=5000)