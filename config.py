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

import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', '5000'))
    DATABASE_PATH = os.environ.get('DATABASE_PATH') or os.path.join(os.path.dirname(__file__), 'pricechecker.db')
    SCRAPING_DELAY = int(os.environ.get('SCRAPING_DELAY', '2'))
    MAX_RETRIES = int(os.environ.get('MAX_RETRIES', '3'))
    TIMEOUT = int(os.environ.get('TIMEOUT', '30'))
    USER_AGENT = os.environ.get('USER_AGENT', 'PriceChecker/2.4.2')

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

@property
def SCRAPING_CONFIG(self):
    return {
        'delay_between_requests': self.SCRAPING_DELAY,
        'timeout': self.TIMEOUT,
        'max_retries': self.MAX_RETRIES,
        'user_agent': self.USER_AGENT,
    }


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