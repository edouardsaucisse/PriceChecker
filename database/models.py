"""
Modèles de base de données pour PriceChecker
Gestion SQLite avec fonctions utilitaires
"""

import sqlite3
import logging
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

def get_latest_prices(product_id):
    """Récupérer les derniers prix pour un produit"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    rows = cursor.execute('''
        SELECT 
            pl.shop_name,
            pl.url,
            ph.price,
            ph.currency,
            ph.is_available,
            ph.error_message,
            ph.scraped_at
        FROM product_links pl
        LEFT JOIN price_history ph ON pl.id = ph.product_link_id
        WHERE pl.product_id = ?
        AND (ph.id IS NULL OR ph.id = (
            SELECT MAX(ph2.id) 
            FROM price_history ph2 
            WHERE ph2.product_link_id = pl.id
        ))
        ORDER BY pl.shop_name
    ''', (product_id,)).fetchall()
    
    conn.close()
    
    # Convertir en liste de dictionnaires
    prices = [dict_from_row(row) for row in rows]
    return prices

def delete_product(product_id):
    """Supprimer un produit et toutes ses données associées"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
    
    conn.commit()
    conn.close()

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