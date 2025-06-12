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