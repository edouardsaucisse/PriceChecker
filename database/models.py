"""
Modèles de base de données pour PriceChecker
Gestion SQLite avec fonctions utilitaires
"""

import sqlite3
import logging
import time
# from datetime import datetime
# from pathlib import Path
# import sys
# import os

from flask import current_app

# Configuration de la base de données
# DATABASE_FILE = "pricechecker.db"

# Configuration du logging
logger = logging.getLogger(__name__)


def get_db_connection():
    """Ouvrir une connexion à la base de données SQLite"""
    try:
        # Utiliser la config Flask si disponible
        if current_app:
            db_path = current_app.config.get('DATABASE_PATH', 'pricechecker.db')
        else:
            db_path = 'pricechecker.db'

        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        logger.error(f"Erreur connexion DB: {e}")
        raise


def dict_from_row(row):
    """Convertir un objet Row SQLite en dictionnaire Python"""
    if row is None:
        return None
    return {key: row[key] for key in row.keys()}


def init_db():
    """Initialiser la base de données avec les tables nécessaires"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Table des produits
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table des liens vers les boutiques
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS product_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            shop_name TEXT NOT NULL,
            url TEXT NOT NULL,
            css_selector TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
        )
    ''')
    
    # Table des prix collectés
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_link_id INTEGER NOT NULL,
            price REAL,
            currency TEXT DEFAULT 'EUR',
            is_available BOOLEAN DEFAULT TRUE,
            error_message TEXT,
            scraped_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_link_id) REFERENCES product_links (id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    
    # Insérer des données de test si aucun produit n'existe
    existing_products = cursor.execute('SELECT COUNT(*) FROM products').fetchone()[0]
    if existing_products == 0:
        print("🌱 Création des données de test...")
        
        # Produit de test 1
        cursor.execute(
            'INSERT INTO products (name, description) VALUES (?, ?)',
            ('iPhone 15 Pro', 'Smartphone Apple dernière génération, 256GB')
        )
        product_id = cursor.lastrowid
        
        # Liens de test
        cursor.execute(
            'INSERT INTO product_links (product_id, shop_name, url) VALUES (?, ?, ?)',
            (product_id, 'Apple Store', 'https://www.apple.com/fr/iphone-15-pro/')
        )
        link_id = cursor.lastrowid
        
        cursor.execute(
            'INSERT INTO product_links (product_id, shop_name, url) VALUES (?, ?, ?)',
            (product_id, 'Amazon', 'https://www.amazon.fr/dp/B0CHX1W1XY')
        )
        link_id_2 = cursor.lastrowid
        
        # Prix de test
        cursor.execute(
            'INSERT INTO price_history (product_link_id, price, currency, is_available) VALUES (?, ?, ?, ?)',
            (link_id, 1229.00, 'EUR', True)
        )
        
        cursor.execute(
            'INSERT INTO price_history (product_link_id, price, currency, is_available) VALUES (?, ?, ?, ?)',
            (link_id_2, 1199.99, 'EUR', True)
        )
        
        # Produit de test 2
        cursor.execute(
            'INSERT INTO products (name, description) VALUES (?, ?)',
            ('Samsung Galaxy S24', 'Smartphone Samsung haut de gamme')
        )
        
        conn.commit()
        print("✅ Données de test créées")
    
    conn.close()
    print("✅ Base de données initialisée")

def create_product(name, description=None):
    """Créer un nouveau produit"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        'INSERT INTO products (name, description) VALUES (?, ?)',
        (name, description)
    )

    product_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return product_id


def update_product(product_id, name, description=None):
    """
    Mettre à jour un produit existant

    Args:
        product_id (int): ID du produit à modifier
        name (str): Nouveau nom du produit
        description (str, optional): Nouvelle description

    Returns:
        bool: True si modifié avec succès, False si produit introuvable

    Raises:
        ValueError: Si le nom est vide
    """
    if not name or name.strip() == "":
        raise ValueError("Le nom du produit ne peut pas être vide")

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Vérifier que le produit existe
        existing = cursor.execute(
            'SELECT id FROM products WHERE id = ?',
            (product_id,)
        ).fetchone()

        if not existing:
            conn.close()
            logger.warning(f"Tentative de modification d'un produit inexistant: {product_id}")
            return False

        # Mettre à jour le produit
        cursor.execute('''
                       UPDATE products
                       SET name        = ?,
                           description = ?,
                           updated_at  = CURRENT_TIMESTAMP
                       WHERE id = ?
                       ''', (name.strip(), description, product_id))

        conn.commit()
        conn.close()

        logger.info(f"Produit {product_id} mis à jour: {name}")
        return True

    except Exception as e:
        conn.close()
        logger.error(f"Erreur lors de la mise à jour du produit {product_id}: {e}")
        raise

def delete_product(product_id):
    """Supprimer un produit et toutes ses données associées"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))

    conn.commit()
    conn.close()

def add_product_link(product_id, shop_name, url, css_selector=None):
    """Ajouter un lien de boutique à un produit"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        'INSERT INTO product_links (product_id, shop_name, url, css_selector) VALUES (?, ?, ?, ?)',
        (product_id, shop_name, url, css_selector)
    )

    link_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return link_id

def get_product_links(product_id):
    """
    Récupérer tous les liens d'un produit (pour affichage/gestion)

    Args:
        product_id (int): ID du produit

    Returns:
        list: Liste des liens avec leurs informations
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    rows = cursor.execute('''
                          SELECT id, shop_name, url, css_selector, created_at
                          FROM product_links
                          WHERE product_id = ?
                          ORDER BY shop_name
                          ''', (product_id,)).fetchall()

    conn.close()

    # Convertir en liste de dictionnaires
    return [dict_from_row(row) for row in rows]

def delete_product_link(link_id):
    """
    Supprimer un lien de boutique spécifique

    Args:
        link_id (int): ID du lien à supprimer

    Returns:
        bool: True si supprimé avec succès, False si lien introuvable
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Vérifier que le lien existe
        existing = cursor.execute(
            'SELECT id, product_id, shop_name FROM product_links WHERE id = ?',
            (link_id,)
        ).fetchone()

        if not existing:
            conn.close()
            logger.warning(f"Tentative de suppression d'un lien inexistant: {link_id}")
            return False

        # Supprimer le lien (les prix associés seront supprimés automatiquement grâce à ON DELETE CASCADE)
        cursor.execute('DELETE FROM product_links WHERE id = ?', (link_id,))

        conn.commit()
        conn.close()

        logger.info(f"Lien supprimé: {existing['shop_name']} pour produit {existing['product_id']}")
        return True

    except Exception as e:
        conn.close()
        logger.error(f"Erreur lors de la suppression du lien {link_id}: {e}")
        raise

def get_all_products():
    """Récupérer tous les produits avec conversion en dictionnaire"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    rows = cursor.execute('''
        SELECT id, name, description, created_at, updated_at 
        FROM products 
        ORDER BY created_at DESC
    ''').fetchall()
    
    conn.close()
    
    # Convertir en liste de dictionnaires
    products = []
    for row in rows:
        product_dict = dict_from_row(row)
        # Traitement des dates pour les templates
        if product_dict['created_at']:
            # Les dates SQLite sont des chaînes, on les garde comme ça pour les templates
            pass
        products.append(product_dict)
    
    return products

def get_product_by_id(product_id):
    """Récupérer un produit par son ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    row = cursor.execute(
        'SELECT id, name, description, created_at, updated_at FROM products WHERE id = ?',
        (product_id,)
    ).fetchone()
    
    conn.close()
    
    return dict_from_row(row) if row else None

def record_price(product_link_id, price, currency='EUR', is_available=True, error_message=None):
    """
    Enregistrer un prix pour un lien de produit

    Args:
        product_link_id (int): ID du lien de produit
        price (float): Prix à enregistrer
        currency (str): Devise du prix (par défaut 'EUR')
        is_available (bool): Disponibilité du produit (par défaut True)
        error_message (str, optional): Message d'erreur en cas d'indisponibilité

    Returns:
        int: ID du nouvel enregistrement de prix
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            '''
            INSERT INTO price_history
            (product_link_id, price, currency, is_available, error_message, scraped_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''',
            (product_link_id, price, currency, is_available, error_message)
        )

        price_history_id = cursor.lastrowid
        conn.commit()
        logger.info(f"Prix enregistré avec succès pour le lien {product_link_id}")
        return price_history_id

    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement du prix pour le lien {product_link_id}: {e}")
        raise

    finally:
        conn.close()

def scrape_all_product_links(product_id):
    """Scraper tous les liens d'un produit"""
    from scraping.price_scraper import create_price_scraper

    links = get_product_links(product_id)
    if not links:
        logger.info(f"Aucun lien à scraper pour le produit {product_id}")
        return []

    scraper = create_price_scraper()
    results = []

    for link in links:
        logger.info(f"Scraping {link['shop_name']} pour produit {product_id}")

        try:
            # Scraper le prix
            price_data = scraper.scrape_price(
                url=link['url'],
                css_selector=link['css_selector'],
                shop_name=link['shop_name']
            )

            # ✅ Utiliser VOTRE fonction record_price
            price_id = record_price(
                product_link_id=link['id'],  # ← Nom correct
                price=price_data['price'],
                currency=price_data['currency'],
                is_available=price_data['is_available'],
                error_message=price_data['error_message']
            )

            result = {
                'link_id': link['id'],
                'shop_name': link['shop_name'],
                'price_id': price_id,
                'success': price_data['is_available'],
                **price_data
            }

            results.append(result)
            time.sleep(1)  # Anti-spam

        except Exception as e:
            logger.error(f"Erreur scraping {link['shop_name']}: {e}")
            results.append({
                'link_id': link['id'],
                'shop_name': link['shop_name'],
                'success': False,
                'error_message': str(e)
            })

    return results

def get_scraping_stats(product_id):
    """
    Statistiques de scraping pour un produit

    Returns:
        dict: Stats du scraping
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    stats = cursor.execute('''
                           SELECT COUNT(*)                                                as total_scrapes,
                                  COUNT(CASE WHEN p.is_available = 1 THEN 1 END)          as successful_scrapes,
                                  COUNT(CASE WHEN p.error_message IS NOT NULL THEN 1 END) as errors,
                                  MAX(p.scraped_at)                                       as last_scrape
                           FROM prices p
                                    JOIN product_links pl ON p.link_id = pl.id
                           WHERE pl.product_id = ?
                           ''', (product_id,)).fetchone()

    conn.close()

    if stats:
        return {
            'total_scrapes': stats['total_scrapes'] or 0,
            'successful_scrapes': stats['successful_scrapes'] or 0,
            'errors': stats['errors'] or 0,
            'last_scrape': stats['last_scrape'],
            'success_rate': round((stats['successful_scrapes'] / max(stats['total_scrapes'], 1)) * 100, 1)
        }

    return {
        'total_scrapes': 0,
        'successful_scrapes': 0,
        'errors': 0,
        'last_scrape': None,
        'success_rate': 0
    }


def get_latest_prices(product_id):
    """Récupérer les derniers prix pour un produit - Version simplifiée"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Récupérer tous les liens du produit
    links = cursor.execute('''
                           SELECT id, shop_name, url, css_selector
                           FROM product_links
                           WHERE product_id = ?
                           ORDER BY shop_name
                           ''', (product_id,)).fetchall()

    prices = []

    # Pour chaque lien, récupérer le dernier prix
    for link in links:
        latest_price = cursor.execute('''
                                      SELECT price, currency, is_available, error_message, scraped_at
                                      FROM price_history
                                      WHERE product_link_id = ?
                                      ORDER BY scraped_at DESC, id DESC LIMIT 1
                                      ''', (link['id'],)).fetchone()

        price_data = {
            'link_id': link['id'],
            'shop_name': link['shop_name'],
            'url': link['url'],
            'css_selector': link['css_selector'],
            'price': None,
            'currency': 'EUR',
            'is_available': False,
            'error_message': None,
            'scraped_at': None
        }

        if latest_price:
            price_data.update({
                'price': latest_price['price'],
                'currency': latest_price['currency'],
                'is_available': latest_price['is_available'],
                'error_message': latest_price['error_message'],
                'scraped_at': latest_price['scraped_at']
            })

        prices.append(price_data)

    conn.close()
    return prices

    # Convertir en liste de dictionnaires avec debug
    prices = []
    for row in rows:
        price_dict = dict_from_row(row)
        logger.debug(f"Prix récupéré pour {price_dict['shop_name']}: {price_dict.get('price', 'Aucun')}")
        prices.append(price_dict)

    return prices

def get_price_history(product_id, limit=50):
    """
    Historique complet des prix pour un produit (pour graphiques futurs)

    Args:
        product_id (int): ID du produit
        limit (int): Nombre maximum d'entrées

    Returns:
        list: Historique des prix
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    rows = cursor.execute('''
                          SELECT ph.*,
                                 pl.shop_name,
                                 pl.url
                          FROM price_history ph
                                   JOIN product_links pl ON ph.product_link_id = pl.id
                          WHERE pl.product_id = ?
                          ORDER BY ph.scraped_at DESC LIMIT ?
                          ''', (product_id, limit)).fetchall()

    conn.close()
    return [dict_from_row(row) for row in rows]

# Test des fonctions
if __name__ == "__main__":
    print("🔧 Test des fonctions de base de données...")
    
    # Initialisation
    init_db()
    
    # Test de récupération des produits
    products = get_all_products()
    print(f"📦 Produits trouvés : {len(products)}")
    
    for product in products:
        print(f"  - {product['name']} (ID: {product['id']})")
        
        # Test des prix
        prices = get_latest_prices(product['id'])
        print(f"    💰 Prix disponibles : {len(prices)}")
        for price in prices:
            if price['price']:
                print(f"      - {price['shop_name']}: {price['price']} {price['currency']}")
            else:
                print(f"      - {price['shop_name']}: Prix non disponible")
    
    print("✅ Tests terminés")