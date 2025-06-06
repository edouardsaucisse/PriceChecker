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