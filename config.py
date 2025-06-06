import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'pricechecker.db')
    
    # Optimisations SQLite
    SQLITE_PRAGMAS = {
        'journal_mode': 'WAL',      # Write-Ahead Logging
        'cache_size': -32000,       # Cache 32MB
        'synchronous': 'NORMAL',    # Performance/sécurité équilibrée
        'temp_store': 'MEMORY',     # Tables temporaires en RAM
        'mmap_size': 268435456,     # Memory-mapped I/O (256MB)
    }
    
    # Fonctionnalités métier
    PRICE_HISTORY_DAYS = 30
    AUTO_UPDATE_ENABLED = True
    AUTO_UPDATE_HOUR = 6

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    # Cache templates en production
    SEND_FILE_MAX_AGE_DEFAULT = 86400  # 24h cache pour assets
    
    # Optimisations production
    SQLITE_PRAGMAS = {
        **Config.SQLITE_PRAGMAS,
        'optimize': True,           # Optimiser à la fermeture
    }

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}