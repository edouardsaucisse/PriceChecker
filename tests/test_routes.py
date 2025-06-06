"""
Tests pour les routes Flask
"""

import pytest
import json
from database.models import create_product

class TestMainRoutes:
    """Tests des routes principales"""

    def test_index_page(self, client):
        """Test page d'accueil"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'PriceChecker' in response.data or b'produits' in response.data

    def test_products_page(self, client):
        """Test page produits"""
        response = client.get('/products')
        assert response.status_code == 200

    def test_add_product_get(self, client):
        """Test affichage formulaire ajout"""
        response = client.get('/add_product')
        assert response.status_code == 200
        assert b'form' in response.data or b'nom' in response.data

    def test_add_product_post_valid(self, client):
        """Test soumission formulaire valide"""
        data = {
            'name': 'Test Product Route',
            'description': 'Description test'
        }
        response = client.post('/add_product', data=data, follow_redirects=True)
        assert response.status_code == 200

    def test_add_product_post_invalid_empty_name(self, client):
        """Test soumission nom vide"""
        data = {
            'name': '',
            'description': 'Description test'
        }
        response = client.post('/add_product', data=data)
        assert response.status_code == 200

    def test_add_product_post_invalid_short_name(self, client):
        """Test nom trop court"""
        data = {
            'name': 'AB',  # Moins de 3 caractères
            'description': 'Description test'
        }
        response = client.post('/add_product', data=data)
        assert response.status_code == 200

class TestProductDetail:
    """Tests détail produit"""

    def test_product_detail_exists(self, client, app, sample_product):
        """Test détail produit existant"""
        with app.app_context():
            product_id = create_product(
                sample_product['name'],
                sample_product['description']
            )

        response = client.get(f'/product/{product_id}')
        assert response.status_code == 200

    def test_product_detail_not_exists(self, client):
        """Test détail produit inexistant"""
        response = client.get('/product/99999', follow_redirects=True)
        assert response.status_code == 200  # Redirection vers products

class TestAPI:
    """Tests API JSON"""

    def test_api_products(self, client):
        """Test API liste produits"""
        response = client.get('/api/products')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert 'status' in data
        assert data['status'] == 'success'
        assert 'products' in data
        assert isinstance(data['products'], list)

    def test_api_product_detail_exists(self, client, app, sample_product):
        """Test API détail produit"""
        with app.app_context():
            product_id = create_product(
                sample_product['name'],
                sample_product['description']
            )

        response = client.get(f'/api/product/{product_id}')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'product' in data
        assert data['product']['name'] == sample_product['name']

    def test_api_product_detail_not_exists(self, client):
        """Test API produit inexistant"""
        response = client.get('/api/product/99999')
        assert response.status_code == 404

        data = json.loads(response.data)
        assert data['status'] == 'error'