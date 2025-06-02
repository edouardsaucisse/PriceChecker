"""
Models pour la base de données PriceCheck

Ce module gère la création et l'interaction avec la base de données SQLite.
Tables: products, product_links, prices

Imports futurs prévus:
- datetime: pour les fonctions d'historique et nettoyage automatique
- os: pour la gestion avancée des fichiers de base
"""

import sqlite3
from config import Config


def get_db_connection():
    """
    Établit une connexion à la base de données SQLite.
    
    Returns:
        sqlite3.Connection: Connexion configurée avec row_factory
    """
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Permet l'accès par nom de colonne
    return conn


def init_db():
    """
    Initialise la base de données avec toutes les tables nécessaires.
    Crée les tables si elles n'existent pas déjà.
    """
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
        description (str): Description optionnelle du produit
        
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
        list: Liste des produits (sqlite3.Row objects)
    """
    conn = get_db_connection()
    products = conn.execute(
        "SELECT * FROM products ORDER BY name"
    ).fetchall()
    conn.close()
    return products


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


def record_price(link_id, price, currency='EUR', is_available=True, error_message=None):
    """
    Enregistre un prix pour un lien produit.
    
    Args:
        link_id (int): ID du lien produit
        price (float): Prix trouvé (peut être None si erreur)
        currency (str): Devise du prix
        is_available (bool): Produit disponible ou non
        error_message (str): Message d'erreur éventuel
        
    Returns:
        int: ID de l'enregistrement de prix créé
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


# Script de test et d'initialisation
if __name__ == '__main__':
    print("🚀 Initialisation de la base de données...")
    init_db()
    
    # Test basique d'insertion
    print("\n📝 Test d'insertion de données...")
    try:
        # Créer un produit de test
        product_id = create_product("iPhone 15 Pro", "Smartphone Apple dernière génération")
        print(f"✓ Produit créé avec l'ID: {product_id}")
        
        # Ajouter un lien de boutique
        link_id = add_product_link(product_id, "Amazon", "https://amazon.fr/iphone-15-pro")
        print(f"✓ Lien boutique créé avec l'ID: {link_id}")
        
        # Enregistrer un prix
        price_id = record_price(link_id, 1199.99, 'EUR', True)
        print(f"✓ Prix enregistré avec l'ID: {price_id}")
        
        # Vérifier les données
        products = get_all_products()
        print(f"✓ Nombre total de produits: {len(products)}")
        
        print("\n🎉 Tests réussis ! Base de données opérationnelle.")
        
    except Exception as e:
        print(f"❌ Erreur lors des tests: {e}")