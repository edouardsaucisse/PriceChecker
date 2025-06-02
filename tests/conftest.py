"""
Configuration pytest pour PriceChecker
"""

import pytest
import tempfile
import os
from app import create_app
from database.models import init_db


@pytest.fixture(scope='session')
def app():
    """Application Flask pour les tests"""
    # Base de données temporaire
    db_fd, db_path = tempfile.mkstemp()

    # Configuration de test
    test_config = {
        'TESTING': True,
        'SECRET_KEY': 'test-secret-key',
        'DATABASE_PATH': db_path,
        'WTF_CSRF_ENABLED': False
    }

    app = create_app('testing')
    app.config.update(test_config)

    with app.app_context():
        init_db()

    yield app

    # Nettoyage
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Client de test Flask"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Runner CLI pour les tests"""
    return app.test_cli_runner()


@pytest.fixture
def sample_product():
    """Données de produit pour les tests"""
    return {
        'name': 'Test Product',
        'description': 'Description de test'
    }


@pytest.fixture
def sample_products():
    """Plusieurs produits pour les tests"""
    return [
        {'name': 'iPhone 15', 'description': 'Smartphone Apple'},
        {'name': 'Galaxy S24', 'description': 'Smartphone Samsung'},
        {'name': 'Pixel 8', 'description': 'Smartphone Google'}
    ]