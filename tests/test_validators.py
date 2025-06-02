"""
Tests pour les validateurs
"""

import pytest
from utils.validators import validate_product_name, validate_url, validate_price

class TestProductNameValidator:
    """Tests validation nom produit"""

    def test_valid_names(self):
        """Test noms valides"""
        valid_names = [
            "iPhone 15",
            "Samsung Galaxy S24",
            "Test Product 123"
        ]

        for name in valid_names:
            is_valid, message = validate_product_name(name)
            assert is_valid, f"'{name}' devrait être valide: {message}"

    def test_invalid_names(self):
        """Test noms invalides"""
        invalid_names = [
            "",           # Vide
            "  ",         # Espaces seulement
            "AB",         # Trop court
            "A" * 101,    # Trop long
            None,         # None
            123           # Pas une string
        ]

        for name in invalid_names:
            is_valid, message = validate_product_name(name)
            assert not is_valid, f"'{name}' devrait être invalide"
            assert message != "", "Message d'erreur requis"

    def validate_product_name(name):
        """Valider le nom d'un produit"""

        # Vérifier que ce n'est pas vide
        if not name or not isinstance(name, str):
            return False, "Le nom est obligatoire"

        # Enlever les espaces
        name = name.strip()

        # Vérifier la longueur minimum
        if len(name) < 3:
            return False, "Le nom doit contenir au moins 3 caractères"

        # Vérifier la longueur maximum
        if len(name) > 100:
            return False, "Le nom ne peut pas dépasser 100 caractères"

        # Vérifier les caractères interdits
        if '<' in name or '>' in name:
            return False, "Le nom ne peut pas contenir < ou >"

        # Tout est bon !
        return True, ""

class TestURLValidator:
    """Tests validation URL"""

    def test_valid_urls(self):
        """Test URLs valides"""
        valid_urls = [
            "https://amazon.fr/product/123",
            "http://example.com",
            "https://shop.example.com/item?id=123"
        ]

        for url in valid_urls:
            is_valid, message = validate_url(url)
            assert is_valid, f"'{url}' devrait être valide: {message}"

    def test_invalid_urls(self):
        """Test URLs invalides"""
        invalid_urls = [
            "",                    # Vide
            "not-an-url",         # Pas une URL
            "ftp://example.com",  # Protocole non supporté
            "://example.com",     # Pas de protocole
            None,                 # None
            123                   # Pas une string
        ]

        for url in invalid_urls:
            is_valid, message = validate_url(url)
            assert not is_valid, f"'{url}' devrait être invalide"

    def validate_shop_url(url):
        """Valider une URL de boutique"""

        if not url:
            return False, "L'URL est obligatoire"

        # Vérifier le format URL
        if not url.startswith(('http://', 'https://')):
            return False, "L'URL doit commencer par http:// ou https://"

        # Vérifier que ce n'est pas suspect
        if 'localhost' in url:
            return False, "Les URLs localhost ne sont pas autorisées"

        # Vérifier la longueur
        if len(url) > 500:
            return False, "URL trop longue"

        return True, ""

class TestPriceValidator:
    """Tests validation prix"""

    def test_valid_prices(self):
        """Test prix valides"""
        valid_prices = [
            0,          # Gratuit
            10.99,      # Prix normal
            1000,       # Prix élevé
            None        # Pas de prix (acceptable)
        ]

        for price in valid_prices:
            is_valid, message = validate_price(price)
            assert is_valid, f"Prix '{price}' devrait être valide: {message}"

    def test_invalid_prices(self):
        """Test prix invalides"""
        invalid_prices = [
            -1,         # Négatif
            1000000,    # Trop élevé
            "abc",      # Pas un nombre
            []          # Type invalide
        ]

        for price in invalid_prices:
            is_valid, message = validate_price(price)
            assert not is_valid, f"Prix '{price}' devrait être invalide"

    def validate_price(price):
        """Valider un prix"""

        # Le prix peut être None (pas encore récupéré)
        if price is None:
            return True, ""

        # Convertir en nombre
        try:
            price_float = float(price)
        except (ValueError, TypeError):
            return False, "Le prix doit être un nombre"

        # Vérifier que ce n'est pas négatif
        if price_float < 0:
            return False, "Le prix ne peut pas être négatif"

        # Vérifier que ce n'est pas absurde
        if price_float > 100000:
            return False, "Prix trop élevé (max 100 000€)"

        return True, ""

    def test_product_name_validation():
        # Test cas valide
        assert validate_product_name("iPhone 15")[0] == True

        # Test cas invalide
        assert validate_product_name("")[0] == False
        assert validate_product_name("AB")[0] == False  # Trop court