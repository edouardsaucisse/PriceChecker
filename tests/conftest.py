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
Configuration pytest pour PriceChecker
"""

import pytest
from app import create_app
from database.models import init_db


@pytest.fixture(scope='session')
def app():
    """Application Flask pour les tests"""
    # Configuration de test simplifiée
    test_config = {
        'TESTING': True,
        'SECRET_KEY': 'test-secret-key',
        'DATABASE_PATH': ':memory:'  # Base en mémoire plus simple
    }

    app = create_app('testing')
    app.config.update(test_config)

    with app.app_context():
        init_db()

    yield app
    # Pas de nettoyage nécessaire avec :memory:


@pytest.fixture
def client(app):
    """Client de test Flask"""
    return app.test_client()


@pytest.fixture
def sample_product():
    """Données de produit pour les tests"""
    return {
        'name': 'Test Product',
        'description': 'Description de test'
    }