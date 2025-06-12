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

from app import create_app

# Créer l'application
app = create_app()

if __name__ == '__main__':
    # L'initialisation de la DB se fait déjà dans create_app() avec le bon contexte
    print("🚀 Lancement de PriceChecker...")
    app.run(debug=True, host='0.0.0.0', port=5000)