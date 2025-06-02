from flask import Flask
from config import config

def create_app(config_name='default'):
    """Factory pour créer l'application Flask"""
    app = Flask(__name__, 
                static_folder='../static',
                static_url_path='/static')
    
    # Charger la configuration depuis config.py
    app.config.from_object(config[config_name])
    
    # Initialiser la base de données automatiquement
    from database.models import init_db
    with app.app_context():
        init_db()
    
    # Enregistrer les blueprints
    from app.routes import main
    app.register_blueprint(main)
    
    return app