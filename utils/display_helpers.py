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

def _get_shop_color(shop_name, alpha=1.0):
    """
    Retourne une couleur pour une boutique donnée

    Args:
        shop_name (str): Nom de la boutique
        alpha (float): Transparence (0.0 à 1.0)

    Returns:
        str: Couleur CSS (rgba ou rgb)
    """
    # Couleurs prédéfinies pour les boutiques connues
    shop_colors = {
        'amazon': '#FF9900',
        'fnac': '#E5B000',
        'cdiscount': '#3732FF',
        'leclerc': '#266AC7',
        'apple': '#000000',
        'darty': '#E60012',
        'boulanger': '#FF6600',
        'carrefour': '#0066CC',
        'auchan': '#FF0000',
        'but': '#C41E3A'
    }

    # Normaliser le nom de la boutique
    normalized_name = shop_name.lower().strip()

    # Chercher une correspondance
    for shop_key, color in shop_colors.items():
        if shop_key in normalized_name:
            if alpha < 1.0:
                # Convertir hex vers rgba
                hex_color = color.lstrip('#')
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                return f'rgba({r}, {g}, {b}, {alpha})'
            return color

    # Couleur par défaut basée sur le hash du nom
    import hashlib
    hash_obj = hashlib.md5(normalized_name.encode())
    hash_hex = hash_obj.hexdigest()

    # Extraire 3 composantes RGB du hash
    r = int(hash_hex[0:2], 16)
    g = int(hash_hex[2:4], 16)
    b = int(hash_hex[4:6], 16)

    if alpha < 1.0:
        return f'rgba({r}, {g}, {b}, {alpha})'
    else:
        return f'rgb({r}, {g}, {b})'