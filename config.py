import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'PriceCheck.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuration des connecteurs
    CONNECTORS_DIR = os.path.join(os.path.dirname(__file__), 'connectors')
    
    # Configuration du scraping
    REQUEST_TIMEOUT = 30
    REQUEST_DELAY = 1  # Délai entre les requêtes en secondes
    MAX_RETRIES = 3
    
    # Configuration de la planification
    AUTO_UPDATE_ENABLED = True
    AUTO_UPDATE_HOUR = 6  # Heure de mise à jour automatique (6h du matin)
    
    # Historique des prix
    PRICE_HISTORY_DAYS = 30

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
