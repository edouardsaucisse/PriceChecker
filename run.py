"""
PriceChecker - Application de surveillance des prix en ligne
Copyright (C) 2024 PriceChecker Project

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

"""
Point d'entrée pour lancer l'application Flask PriceChecker
"""

import os
from dotenv import load_dotenv
from app import create_app

# Charger les variables du fichier .env
load_dotenv()

# Créer l'application
app = create_app()

if __name__ == '__main__':
    print("🚀 Lancement de PriceChecker...")

    # Récupérer la configuration depuis les variables d'environnement
    debug_mode = os.environ.get('DEBUG', 'True').lower() == 'true'
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', '5000'))

    app.run(debug=debug_mode, host=host, port=port)