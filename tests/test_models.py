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
Tests pour les modèles de base de données
"""

import pytest
from database.models import (
    init_db, get_all_products, create_product,
    get_product_by_id, add_product_link, get_latest_prices
)


class TestDatabaseInit:
    """Tests d'initialisation de la base"""

    def test_init_db_creates_tables(self, app):
        """Test que init_db crée bien les tables"""
        with app.app_context():
            init_db()
            # Vérifier que les tables existent
            products = get_all_products()
            assert isinstance(products, list)


class TestProductCRUD:
    """Tests CRUD pour les produits"""

    def test_create_product_success(self, app, sample_product):
        """Test création d'un produit"""
        with app.app_context():
            product_id = create_product(
                sample_product['name'],
                sample_product['description']
            )
            assert isinstance(product_id, int)
            assert product_id > 0

    def test_create_product_name_only(self, app):
        """Test création produit avec nom seulement"""
        with app.app_context():
            product_id = create_product("Test Name Only")
            assert isinstance(product_id, int)

    def test_get_all_products_empty(self, app):
        """Test récupération produits base vide"""
        with app.app_context():
            # Nettoyer d'abord
            products = get_all_products()
            # Devrait retourner liste vide ou produits de test
            assert isinstance(products, list)

    def test_get_product_by_id_exists(self, app, sample_product):
        """Test récupération produit existant"""
        with app.app_context():
            # Créer un produit
            product_id = create_product(
                sample_product['name'],
                sample_product['description']
            )

            # Le récupérer
            product = get_product_by_id(product_id)
            assert product is not None
            assert product['name'] == sample_product['name']
            assert product['description'] == sample_product['description']

    def test_get_product_by_id_not_exists(self, app):
        """Test récupération produit inexistant"""
        with app.app_context():
            product = get_product_by_id(99999)
            assert product is None


class TestProductLinks:
    """Tests pour les liens de produits"""

    def test_add_product_link(self, app, sample_product):
        """Test ajout lien de boutique"""
        with app.app_context():
            # Créer un produit
            product_id = create_product(
                sample_product['name'],
                sample_product['description']
            )

            # Ajouter un lien
            link_id = add_product_link(
                product_id,
                "Amazon",
                "https://amazon.fr/test"
            )
            assert isinstance(link_id, int)
            assert link_id > 0

    def test_get_latest_prices_no_prices(self, app, sample_product):
        """Test récupération prix sans historique"""
        with app.app_context():
            # Créer un produit
            product_id = create_product(
                sample_product['name'],
                sample_product['description']
            )

            # Récupérer les prix
            prices = get_latest_prices(product_id)
            assert isinstance(prices, list)
            # Peut être vide ou contenir des liens sans prix