"""
Application Flask pour PriceChecker
"""

from flask import Flask
import os


def create_app():
    """Factory pour créer l'application Flask"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
    app.config['DATABASE_PATH'] = 'pricechecker.db'
    
    # Import des routes
    from app.routes import main
    app.register_blueprint(main)
    
    return app