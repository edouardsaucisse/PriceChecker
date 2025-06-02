"""
Validateurs pour PriceChecker
"""

# import re
from urllib.parse import urlparse

def validate_product_name(name):
    """Valider le nom d'un produit"""
    if not name or not isinstance(name, str):
        return False, "Le nom est obligatoire"
    
    name = name.strip()
    if len(name) < 3:
        return False, "Le nom doit contenir au moins 3 caractères"
    
    if len(name) > 100:
        return False, "Le nom ne peut pas dépasser 100 caractères"
    
    return True, ""

def validate_url(url):
    """Valider une URL"""
    if not url or not isinstance(url, str):
        return False, "L'URL est obligatoire"
    
    try:
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            return False, "URL invalide"
        
        if result.scheme not in ['http', 'https']:
            return False, "Seules les URLs HTTP/HTTPS sont acceptées"
        
        return True, ""
    except Exception:
        return False, "Format d'URL invalide"

def validate_price(price):
    """Valider un prix"""
    if price is None:
        return True, ""  # Prix peut être None
    
    try:
        price_float = float(price)
        if price_float < 0:
            return False, "Le prix ne peut pas être négatif"
        
        if price_float > 999999:
            return False, "Prix trop élevé"
        
        return True, ""
    except (ValueError, TypeError):
        return False, "Format de prix invalide"