"""
Models pour la base de données Pricechecker

Ce module gère la création et l'interaction avec la base de données SQLite.
Tables: products, product_links, prices
"""

import sqlite3
import os
import sys

# Import config : solution propre selon le contexte d'exécution
if __name__ == '__main__':
    # Si exécuté directement, ajuster le path temporairement
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if root_dir not in sys.path:
        sys.path.insert(0, root_dir)

from config import Config


def get_db_connection():
    """
    Établit une connexion à la base de données SQLite.
    
    Returns:
        sqlite3.Connection: Connexion configurée avec row_factory
    """
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Initialise la base de données avec toutes les tables nécessaires.
    """
    print(f"📁 Création de la base de données : {Config.DATABASE_PATH}")
    
    conn = get_db_connection()
    
    # Table des produits à surveiller
    conn.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table des liens vers les boutiques pour chaque produit
    conn.execute('''
        CREATE TABLE IF NOT EXISTS product_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            shop_name TEXT NOT NULL,
            url TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
        )
    ''')
    
    # Table de l'historique des prix
    conn.execute('''
        CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            link_id INTEGER NOT NULL,
            price DECIMAL(10,2),
            currency TEXT DEFAULT 'EUR',
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_available BOOLEAN DEFAULT TRUE,
            error_message TEXT,
            FOREIGN KEY (link_id) REFERENCES product_links (id) ON DELETE CASCADE
        )
    ''')
    
    # Index pour optimiser les requêtes fréquentes
    conn.execute('CREATE INDEX IF NOT EXISTS idx_prices_scraped_at ON prices (scraped_at)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_prices_link_id ON prices (link_id)')
    
    conn.commit()
    conn.close()
    print("✓ Base de données initialisée avec succès")


def create_product(name, description=""):
    """
    Crée un nouveau produit dans la base de données.
    
    Args:
        name (str): Nom du produit
        description (str): Description optionnelle
        
    Returns:
        int: ID du produit créé
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO products (name, description) VALUES (?, ?)",
        (name, description)
    )
    product_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return product_id


def get_all_products():
    """
    Récupère tous les produits de la base de données.
    
    Returns:
        list: Liste des produits avec leurs informations
    """
    conn = get_db_connection()
    products = conn.execute(
        "SELECT * FROM products ORDER BY name"
    ).fetchall()
    conn.close()
    return products


def get_product_by_id(product_id):
    """
    Récupère un produit par son ID.
    
    Args:
        product_id (int): ID du produit
        
    Returns:
        sqlite3.Row or None: Données du produit
    """
    conn = get_db_connection()
    product = conn.execute(
        "SELECT * FROM products WHERE id = ?", (product_id,)
    ).fetchone()
    conn.close()
    return product


def add_product_link(product_id, shop_name, url):
    """
    Ajoute un lien de boutique pour un produit.
    
    Args:
        product_id (int): ID du produit
        shop_name (str): Nom de la boutique
        url (str): URL du produit sur la boutique
        
    Returns:
        int: ID du lien créé
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO product_links (product_id, shop_name, url) VALUES (?, ?, ?)",
        (product_id, shop_name, url)
    )
    link_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return link_id


def get_product_links(product_id):
    """
    Récupère tous les liens d'un produit.
    
    Args:
        product_id (int): ID du produit
        
    Returns:
        list: Liste des liens du produit
    """
    conn = get_db_connection()
    links = conn.execute(
        "SELECT * FROM product_links WHERE product_id = ?", (product_id,)
    ).fetchall()
    conn.close()
    return links


def record_price(link_id, price, currency='EUR', is_available=True, error_message=None):
    """
    Enregistre un prix pour un lien produit.
    
    Args:
        link_id (int): ID du lien produit
        price (float): Prix du produit
        currency (str): Devise
        is_available (bool): Disponibilité du produit
        error_message (str): Message d'erreur éventuel
        
    Returns:
        int: ID du prix enregistré
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO prices (link_id, price, currency, is_available, error_message) 
           VALUES (?, ?, ?, ?, ?)""",
        (link_id, price, currency, is_available, error_message)
    )
    price_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return price_id


def get_latest_prices(product_id):
    """
    Récupère les derniers prix d'un produit pour toutes les boutiques.
    
    Args:
        product_id (int): ID du produit
        
    Returns:
        list: Derniers prix par boutique
    """
    conn = get_db_connection()
    prices = conn.execute("""
        SELECT 
            pl.shop_name,
            pl.url,
            p.price,
            p.currency,
            p.is_available,
            p.scraped_at,
            p.error_message
        FROM product_links pl
        LEFT JOIN prices p ON pl.id = p.link_id
        WHERE pl.product_id = ?
        AND p.scraped_at = (
            SELECT MAX(scraped_at) 
            FROM prices p2 
            WHERE p2.link_id = pl.id
        )
        ORDER BY pl.shop_name
    """, (product_id,)).fetchall()
    conn.close()
    return prices


def get_price_history(link_id, limit=30):
    """
    Récupère l'historique des prix pour un lien.
    
    Args:
        link_id (int): ID du lien
        limit (int): Nombre maximum d'entrées
        
    Returns:
        list: Historique des prix
    """
    conn = get_db_connection()
    prices = conn.execute("""
        SELECT price, currency, is_available, scraped_at, error_message
        FROM prices 
        WHERE link_id = ?
        ORDER BY scraped_at DESC
        LIMIT ?
    """, (link_id, limit)).fetchall()
    conn.close()
    return prices


# Script de test et d'initialisation
if __name__ == '__main__':
    print("🏗️  Initialisation de la base de données PriceChecker...")
    init_db()
    
    # Test d'insertion de données
    print("\n🧪 Tests d'insertion de données...")
    try:
        # Créer un produit de test
        product_id = create_product(
            "iPhone 15 Pro", 
            "Smartphone Apple dernière génération - 256GB"
        )
        print(f"✓ Produit créé avec l'ID: {product_id}")
        
        # Ajouter plusieurs liens de boutiques
        amazon_link = add_product_link(
            product_id, 
            "Amazon", 
            "https://amazon.fr/apple-iphone-15-pro"
        )
        fnac_link = add_product_link(
            product_id, 
            "Fnac", 
            "https://fnac.com/apple-iphone-15-pro"
        )
        print(f"✓ Liens boutiques créés: Amazon({amazon_link}), Fnac({fnac_link})")
        
        # Enregistrer des prix
        amazon_price = record_price(amazon_link, 1199.99, 'EUR', True)
        fnac_price = record_price(fnac_link, 1249.00, 'EUR', True)
        print(f"✓ Prix enregistrés: Amazon({amazon_price}), Fnac({fnac_price})")
        
        # Vérifications
        products = get_all_products()
        print(f"✓ Nombre total de produits: {len(products)}")
        
        latest_prices = get_latest_prices(product_id)
        print(f"✓ Derniers prix récupérés: {len(latest_prices)} boutiques")
        
        for price_info in latest_prices:
            if price_info['price']:
                print(f"  • {price_info['shop_name']}: {price_info['price']} {price_info['currency']}")
        
        print("\n🎉 Tous les tests sont réussis ! Base de données opérationnelle.")
        
    except Exception as e:
        print(f"❌ Erreur lors des tests: {e}")
        import traceback
        traceback.print_exc()