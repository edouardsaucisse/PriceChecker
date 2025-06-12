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

from flask import Flask
from config import config
from flask_moment import Moment

moment = Moment()

def create_app(config_name='default'):
    """Factory pour créer l'application Flask"""
    app = Flask(__name__, 
                static_folder='../static',
                static_url_path='/static')

    app.config.from_object(config[config_name])

    moment.init_app(app)

    from database.models import init_db
    with app.app_context():
        init_db()
    
    # Enregistrer les blueprints
    from app.routes import main
    app.register_blueprint(main)
    
    return app