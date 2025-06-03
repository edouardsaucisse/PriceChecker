
"""
Tests pour les validateurs PriceChecker
"""

import pytest
from utils.validators import (
    validate_product_name,
    validate_product_description,
    validate_shop_url,
    validate_shop_name,
    validate_price,
    validate_css_selector,
    validate_all_product_data,
    validate_all_link_data
)

class TestProductNameValidator:
    """Tests pour validation nom produit"""
    
    def test_valid_names(self):
        """Test noms valides"""
        valid_names = [
            "iPhone 15",
            "Samsung Galaxy S24",
            "Test Product 123",
            "Produit-Test_2024",
            "Nintendo Switch OLED"
        ]
        
        for name in valid_names:
            is_valid, message = validate_product_name(name)
            assert is_valid, f"'{name}' devrait être valide: {message}"
            assert message == ""
    
    def test_invalid_names(self):
        """Test noms invalides"""
        test_cases = [
            ("", "Le nom est obligatoire"),
            ("  ", "Le nom doit contenir au moins un caractère alphanunérique"),
            ("AB", "Le nom doit contenir au moins 3 caractères"),
            ("A" * 101, "Le nom ne peut pas dépasser 100 caractères"),
            (None, "Le nom est obligatoire"),
            (123, "Le nom est obligatoire"),
            ("Test<script>", "Le nom contient des caractères non autorisés"),
            ("Test>alert", "Le nom contient des caractères non autorisés"),
            ("Test\"quote", "Le nom contient des caractères non autorisés"),
            ("Test&amp;", "Le nom contient des caractères non autorisés"),
            ("---", "Le nom doit contenir au moins un caractère alphanunérique")
        ]
        
        for name, expected_error in test_cases:
            is_valid, message = validate_product_name(name)
            assert not is_valid, f"'{name}' devrait être invalide"
            assert expected_error in message, f"Message incorrect pour '{name}': {message}"

class TestProductDescriptionValidator:
    """Tests pour validation description produit"""
    
    def test_valid_descriptions(self):
        """Test descriptions valides"""
        valid_descriptions = [
            None,  # Description optionnelle
            "",    # Description vide
            "Description simple",
            "Description avec des chiffres 123",
            "Description-avec_caractères spéciaux! (OK)",
            "A" * 500  # Longueur maximum
        ]
        
        for desc in valid_descriptions:
            is_valid, message = validate_product_description(desc)
            assert is_valid, f"Description '{desc}' devrait être valide: {message}"
    
    def test_invalid_descriptions(self):
        """Test descriptions invalides"""
        test_cases = [
            ("A" * 501, "La description ne peut pas dépasser 500 caractères"),
            ("<script>alert('test')</script>", "La description contient du contenu non autorisé"),
            ("Test <iframe>", "La description contient du contenu non autorisé"),
            ("javascript:alert(1)", "La description contient du contenu non autorisé"),
            (123, "La description doit être du texte")
        ]
        
        for desc, expected_error in test_cases:
            is_valid, message = validate_product_description(desc)
            assert not is_valid, f"Description '{desc}' devrait être invalide"
            assert expected_error in message

class TestShopURLValidator:
    """Tests pour validation URL boutique"""
    
    def test_valid_urls(self):
        """Test URLs valides"""
        valid_urls = [
            "https://amazon.fr/product/123",
            "http://example.com",
            "https://shop.example.com/item?id=123&color=red",
            "https://www.fnac.com/test",
            "http://boutique-test.fr/produit"
        ]
        
        for url in valid_urls:
            is_valid, message = validate_shop_url(url)
            assert is_valid, f"URL '{url}' devrait être valide: {message}"
    
    def test_invalid_urls(self):
        """Test URLs invalides"""
        test_cases = [
            ("", "L'URL est obligatoire"),
            (None, "L'URL est obligatoire"),
            ("not-an-url", "L'URL doit commencer par http:// ou https://"),
            ("ftp://example.com", "L'URL doit commencer par http:// ou https://"),
            ("://example.com", "L'URL doit commencer par http:// ou https://"),
            ("https://", "URL invalide : domaine manquant"),
            ("http://localhost/test", "Cette URL n'est pas autorisée"),
            ("https://127.0.0.1/test", "Cette URL n'est pas autorisée"),
            ("A" * 2001, "L'URL est trop longue"),
            (123, "L'URL est obligatoire")
        ]
        
        for url, expected_error in test_cases:
            is_valid, message = validate_shop_url(url)
            assert not is_valid, f"URL '{url}' devrait être invalide"
            assert expected_error in message

class TestShopNameValidator:
    """Tests pour validation nom boutique"""
    
    def test_valid_shop_names(self):
        """Test noms boutiques valides"""
        valid_names = [
            "Amazon",
            "Fnac",
            "E.Leclerc",
            "Shop-Test",
            "Boutique_2024"
        ]
        
        for name in valid_names:
            is_valid, message = validate_shop_name(name)
            assert is_valid, f"Nom '{name}' devrait être valide: {message}"
    
    def test_invalid_shop_names(self):
        """Test noms boutiques invalides"""
        test_cases = [
            ("", "Le nom de la boutique est obligatoire"),
            ("A", "Le nom de la boutique doit contenir au moins 2 caractères"),
            ("A" * 51, "Le nom de la boutique ne peut pas dépasser 50 caractères"),
            ("Test<script>", "Le nom de la boutique contient des caractères non autorisés"),
            (None, "Le nom de la boutique est obligatoire")
        ]
        
        for name, expected_error in test_cases:
            is_valid, message = validate_shop_name(name)
            assert not is_valid, f"Nom '{name}' devrait être invalide"
            assert expected_error in message

class TestPriceValidator:
    """Tests pour validation prix"""
    
    def test_valid_prices(self):
        """Test prix valides"""
        valid_prices = [
            None,       # Pas de prix
            "",         # Prix vide
            0,          # Gratuit
            10.99,      # Prix normal
            1000,       # Prix élevé
            "15.50",    # String prix
            "99,99",    # Prix avec virgule
            "25€",      # Prix avec symbole
            " 30.00 "   # Prix avec espaces
        ]
        
        for price in valid_prices:
            is_valid, message = validate_price(price)
            assert is_valid, f"Prix '{price}' devrait être valide: {message}"
    
    def test_invalid_prices(self):
        """Test prix invalides"""
        test_cases = [
            (-1, "Le prix ne peut pas être négatif"),
            (-10.5, "Le prix ne peut pas être négatif"),
            (1000001, "Prix trop élevé"),
            ("abc", "Format de prix invalide"),
            ("--15", "Format de prix invalide"),
            ([], "Format de prix invalide"),
            (10.999, "Le prix ne peut avoir que 2 décimales maximum")
        ]
        
        for price, expected_error in test_cases:
            is_valid, message = validate_price(price)
            assert not is_valid, f"Prix '{price}' devrait être invalide"
            assert expected_error in message

class TestCSSelectorValidator:
    """Tests pour validation sélecteur CSS"""
    
    def test_valid_selectors(self):
        """Test sélecteurs CSS valides"""
        valid_selectors = [
            ".price",
            "#product-price",
            "span.price-current",
            "div.product-info > span.price",
            "[data-price]",
            ".price:first-child"
        ]
        
        for selector in valid_selectors:
            is_valid, message = validate_css_selector(selector)
            assert is_valid, f"Sélecteur '{selector}' devrait être valide: {message}"
    
    def test_invalid_selectors(self):
        """Test sélecteurs CSS invalides"""
        test_cases = [
            ("", "Le sélecteur CSS est obligatoire"),
            (None, "Le sélecteur CSS est obligatoire"),
            ("A" * 201, "Le sélecteur est trop long"),
            ("script", "Le sélecteur contient du code non autorisé"),
            ("javascript:alert(1)", "Le sélecteur contient du code non autorisé"),
            ("eval(test)", "Le sélecteur contient du code non autorisé"),
            ("test{background:url()}", "Format de sélecteur CSS invalide")
        ]
        
        for selector, expected_error in test_cases:
            is_valid, message = validate_css_selector(selector)
            assert not is_valid, f"Sélecteur '{selector}' devrait être invalide"
            assert expected_error in message

class TestCombinedValidators:
    """Tests pour les validateurs combinés"""
    
    def test_validate_all_product_data_valid(self):
        """Test validation complète produit valide"""
        is_valid, errors = validate_all_product_data("iPhone 15", "Smartphone Apple")
        assert is_valid
        assert len(errors) == 0
    
    def test_validate_all_product_data_invalid(self):
        """Test validation complète produit invalide"""
        is_valid, errors = validate_all_product_data("", "A" * 501)
        assert not is_valid
        assert len(errors) == 2
        assert any("nom" in error.lower() for error in errors)
        assert any("description" in error.lower() for error in errors)
    
    def test_validate_all_link_data_valid(self):
        """Test validation complète lien valide"""
        is_valid, errors = validate_all_link_data(
            1, "Amazon", "https://amazon.fr/test", ".price"
        )
        assert is_valid
        assert len(errors) == 0
    
    def test_validate_all_link_data_invalid(self):
        """Test validation complète lien invalide"""
        is_valid, errors = validate_all_link_data(
            -1, "", "not-url", "javascript:alert(1)"
        )
        assert not is_valid
        assert len(errors) == 4  # ID, shop, URL, sélecteur