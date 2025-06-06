"""
Validateurs pour PriceChecker
Fonctions de validation des données utilisateur
"""

import re
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)


def validate_product_name(name):
    """
    Valider le nom d'un produit

    Args:
        name: Nom du produit à valider

    Returns:
        tuple: (is_valid: bool, error_message: str)
    """
    if not name or not isinstance(name, str):
        return False, "Le nom est obligatoire"

    # Nettoyer les espaces
    name = name.strip()

    # ✅ CORRECTION 1: Vérifier d'abord le contenu alphanumétrique
    # Ceci permet de gérer les cas comme "  " ou "---" avant la longueur
    if not re.search(r'[a-zA-Z0-9]', name):
        return False, "Le nom doit contenir au moins un caractère alphanunérique"

    # Vérifier la longueur minimum
    if len(name) < 3:
        return False, "Le nom doit contenir au moins 3 caractères"

    # Vérifier la longueur maximum
    if len(name) > 100:
        return False, "Le nom ne peut pas dépasser 100 caractères"

    # Vérifier les caractères dangereux (XSS basique)
    dangerous_chars = ['<', '>', '"', "'", '&']
    if any(char in name for char in dangerous_chars):
        return False, "Le nom contient des caractères non autorisés"

    return True, ""


def validate_product_description(description):
    """
    Valider la description d'un produit

    Args:
        description: Description du produit (peut être None)

    Returns:
        tuple: (is_valid: bool, error_message: str)
    """
    # La description est optionnelle
    if description is None or description == "":
        return True, ""

    if not isinstance(description, str):
        return False, "La description doit être du texte"

    # Nettoyer les espaces
    description = description.strip()

    # Vérifier la longueur maximum
    if len(description) > 500:
        return False, "La description ne peut pas dépasser 500 caractères"

    # Vérifier les caractères dangereux
    dangerous_chars = ['<script', '</script>', '<iframe', 'javascript:']
    description_lower = description.lower()
    if any(char in description_lower for char in dangerous_chars):
        return False, "La description contient du contenu non autorisé"

    return True, ""


def validate_shop_url(url):
    """
    Valider une URL de boutique en ligne

    Args:
        url: URL à valider

    Returns:
        tuple: (is_valid: bool, error_message: str)
    """
    if not url or not isinstance(url, str):
        return False, "L'URL est obligatoire"

    # Nettoyer les espaces
    url = url.strip()

    # Vérifier la longueur
    if len(url) > 2000:
        return False, "L'URL est trop longue (max 2000 caractères)"

    try:
        # Parser l'URL
        parsed = urlparse(url)

        # Vérifier le schéma
        if parsed.scheme not in ['http', 'https']:
            return False, "L'URL doit commencer par http:// ou https://"

        # Vérifier qu'il y a un domaine
        if not parsed.netloc:
            return False, "URL invalide : domaine manquant"

        # Vérifier les URLs suspectes
        suspicious_domains = ['localhost', '127.0.0.1', '0.0.0.0', 'file://', 'ftp://']
        if any(suspicious in url.lower() for suspicious in suspicious_domains):
            return False, "Cette URL n'est pas autorisée"

        # Vérifier les domaines de boutiques connues (optionnel)
        #valid_domains = [
        #    'amazon.', 'ebay.', 'cdiscount.', 'fnac.', 'darty.',
        #    'boulanger.', 'leclerc.', 'carrefour.', 'auchan.',
        #    'shop.', 'store.', 'boutique.'
        #]
        # Note: Cette vérification est optionnelle et peut être supprimée
        # si vous voulez accepter tous les domaines

        return True, ""

    except Exception as e:
        logger.error(f"Erreur validation URL: {e}")
        return False, "Format d'URL invalide"


def validate_shop_name(shop_name):
    """
    Valider le nom d'une boutique

    Args:
        shop_name: Nom de la boutique

    Returns:
        tuple: (is_valid: bool, error_message: str)
    """
    if not shop_name or not isinstance(shop_name, str):
        return False, "Le nom de la boutique est obligatoire"

    # Nettoyer les espaces
    shop_name = shop_name.strip()

    # Vérifier la longueur
    if len(shop_name) < 2:
        return False, "Le nom de la boutique doit contenir au moins 2 caractères"

    if len(shop_name) > 50:
        return False, "Le nom de la boutique ne peut pas dépasser 50 caractères"

    # Vérifier les caractères dangereux
    dangerous_chars = ['<', '>', '"', "'", '&']
    if any(char in shop_name for char in dangerous_chars):
        return False, "Le nom de la boutique contient des caractères non autorisés"

    return True, ""


def validate_price(price):
    """
    Valider un prix

    Args:
        price: Prix à valider (peut être None, string ou number)

    Returns:
        tuple: (is_valid: bool, error_message: str)
    """
    # Le prix peut être None (pas encore récupéré)
    if price is None or price == "":
        return True, ""

    try:
        # Convertir en float
        if isinstance(price, str):
            # Nettoyer les espaces d'abord
            price = price.strip()

            # ✅ CORRECTION SIMPLE: Vérifier les patterns invalides AVANT tout traitement
            # Détecter les doubles signes comme "--15", "++10", etc.
            if '--' in price or '++' in price or '+-' in price or '-+' in price:
                return False, "Format de prix invalide"

            # Vérifier qu'il y a au moins un chiffre
            if not re.search(r'\d', price):
                return False, "Format de prix invalide"

            # Nettoyer la string (enlever espaces, €, etc. SAUF les signes)
            price_clean = re.sub(r'[^\d.,+-]', '', price)
            price_clean = price_clean.replace(',', '.')

            # Si après nettoyage il ne reste rien, c'est invalide
            if not price_clean:
                return False, "Format de prix invalide"

            price_float = float(price_clean)
        else:
            price_float = float(price)

        # Vérifier que ce n'est pas négatif
        if price_float < 0:
            return False, "Le prix ne peut pas être négatif"

        # Vérifier que ce n'est pas absurde
        if price_float > 1000000:
            return False, "Prix trop élevé (maximum 1 000 000€)"

        # Vérifier la précision (max 2 décimales)
        if round(price_float, 2) != price_float:
            return False, "Le prix ne peut avoir que 2 décimales maximum"

        return True, ""

    except (ValueError, TypeError) as e:
        logger.error(f"Erreur conversion prix: {e}")
        return False, "Format de prix invalide"


def validate_css_selector(selector):
    """
    Valider un sélecteur CSS pour le scraping

    Args:
        selector: Sélecteur CSS

    Returns:
        tuple: (is_valid: bool, error_message: str)
    """
    if not selector or not isinstance(selector, str):
        return False, "Le sélecteur CSS est obligatoire"

    # Nettoyer les espaces
    selector = selector.strip()

    # Vérifier la longueur
    if len(selector) < 1:
        return False, "Le sélecteur ne peut pas être vide"

    if len(selector) > 200:
        return False, "Le sélecteur est trop long (max 200 caractères)"

    # Vérifications basiques de sécurité
    dangerous_patterns = ['script', 'javascript:', 'eval(', 'function(']
    selector_lower = selector.lower()
    if any(pattern in selector_lower for pattern in dangerous_patterns):
        return False, "Le sélecteur contient du code non autorisé"

    # Vérifier que ça ressemble à un sélecteur CSS
    css_pattern = r'^[a-zA-Z0-9\s\.\#\[\]\-_:>,\(\)="\']+$'
    if not re.match(css_pattern, selector):
        return False, "Format de sélecteur CSS invalide"

    return True, ""


def validate_all_product_data(name, description=None):
    """
    Valider toutes les données d'un produit en une fois

    Args:
        name: Nom du produit
        description: Description du produit (optionnelle)

    Returns:
        tuple: (is_valid: bool, error_messages: list)
    """
    errors = []

    # Valider le nom
    name_valid, name_error = validate_product_name(name)
    if not name_valid:
        errors.append(name_error)

    # Valider la description si fournie
    if description is not None:
        desc_valid, desc_error = validate_product_description(description)
        if not desc_valid:
            errors.append(desc_error)

    return len(errors) == 0, errors


def validate_all_link_data(product_id, shop_name, url, css_selector=None):
    """
    Valider toutes les données d'un lien de produit

    Args:
        product_id: ID du produit
        shop_name: Nom de la boutique
        url: URL du produit
        css_selector: Sélecteur CSS (optionnel)

    Returns:
        tuple: (is_valid: bool, error_messages: list)
    """
    errors = []

    # Valider l'ID produit
    if not isinstance(product_id, int) or product_id <= 0:
        errors.append("ID produit invalide")

    # Valider le nom de la boutique
    shop_valid, shop_error = validate_shop_name(shop_name)
    if not shop_valid:
        errors.append(shop_error)

    # Valider l'URL
    url_valid, url_error = validate_shop_url(url)
    if not url_valid:
        errors.append(url_error)

    # Valider le sélecteur CSS si fourni
    if css_selector:
        selector_valid, selector_error = validate_css_selector(css_selector)
        if not selector_valid:
            errors.append(selector_error)

    return len(errors) == 0, errors