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
Modèles de base de données pour PriceChecker
Gestion SQLite avec fonctions utilitaires
"""

import sqlite3
import logging
import time

import utils.display_helpers

from flask import current_app

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

        if hasattr(current_app.config, 'SQLITE_PRAGMAS'):
            for pragma, value in current_app.config.SQLITE_PRAGMAS.items():
                conn.execute(f"PRAGMA {pragma} = {value}")

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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')

    # Table des liens vers les boutiques
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS product_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            shop_name TEXT NOT NULL,
            url TEXT NOT NULL,
            css_selector TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
        );
    ''')

    # Table des prix collectés
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_link_id INTEGER NOT NULL,
            price REAL,
            currency TEXT DEFAULT 'EUR',
            is_available BOOLEAN DEFAULT 1,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            error_message TEXT,
            FOREIGN KEY (product_link_id) REFERENCES product_links (id) ON DELETE CASCADE
        )
    ''')

# Index pour accélérer les requêtes sur les prix
    conn.commit()
    conn.close()
    print("✅ Base de données initialisée")

"""PRODUCTS"""
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

def delete_product(product_id):
    """
    Supprimer un produit et toutes ses données associées (liens + prix)

    Args:
        product_id (int): ID du produit à supprimer

    Returns:
        bool: True si supprimé avec succès, False si produit introuvable

    Raises:
        Exception: En cas d'erreur lors de la suppression
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 1. Vérifier que le produit existe
        existing_product = cursor.execute(
            'SELECT id, name FROM products WHERE id = ?',
            (product_id,)
        ).fetchone()

        if not existing_product:
            conn.close()
            logger.warning(f"Tentative de suppression d'un produit inexistant: {product_id}")
            return False

        product_name = existing_product['name']

        # 2. Récupérer les IDs des liens pour supprimer les prix
        link_ids = cursor.execute(
            'SELECT id FROM product_links WHERE product_id = ?',
            (product_id,)
        ).fetchall()

        # 3. Supprimer tous les prix associés aux liens
        if link_ids:
            link_ids_list = [row['id'] for row in link_ids]
            placeholders = ','.join('?' * len(link_ids_list))
            cursor.execute(
                f'DELETE FROM price_history WHERE product_link_id IN ({placeholders})',
                link_ids_list
            )
            deleted_prices = cursor.rowcount
            logger.info(f"Supprimés {deleted_prices} prix pour le produit {product_id}")

        # 4. Supprimer tous les liens du produit
        cursor.execute('DELETE FROM product_links WHERE product_id = ?', (product_id,))
        deleted_links = cursor.rowcount
        logger.info(f"Supprimés {deleted_links} liens pour le produit {product_id}")

        # 5. Supprimer le produit lui-même
        cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))

        # 6. Valider toutes les suppressions
        conn.commit()
        conn.close()

        logger.info(f"Produit supprimé avec succès: {product_name} (ID: {product_id})")
        return True

    except Exception as e:
        conn.rollback()  # Annuler en cas d'erreur
        conn.close()
        logger.error(f"Erreur lors de la suppression du produit {product_id}: {e}")
        raise

"""LINKS"""
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

"""SCRAPING"""
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

"""PRICES"""
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
            'url': link['url'],              # ✅ URL présente ici
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
    # Filtrer les prix disponibles
    available_prices = [price for price in prices if price['is_available'] and price['price'] is not None]

    # Trouver le meilleur prix
    best_price = None
    if available_prices:
        best_price = min(available_prices, key=lambda x: x['price'])
        # ✅ best_price contient maintenant AUSSI l'URL !

    return {
        'prices': prices,
        'best_price': best_price
    }

    # Convertir en liste de dictionnaires avec debug
    #prices = []
    #for row in rows:
    #    price_dict = dict_from_row(row)
    #    logger.debug(f"Prix récupéré pour {price_dict['shop_name']}: {price_dict.get('price', 'Aucun')}")
    #    prices.append(price_dict)

    #return prices

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

def get_price_history_data(product_id, days=30):
    """
    Récupérer les données d'historique pour les graphiques

    Args:
        product_id (int): ID du produit
        days (int): Nombre de jours d'historique (par défaut 30)

    Returns:
        dict: Données formatées pour Chart.js
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Récupérer l'historique par boutique
    rows = cursor.execute('''
                          SELECT pl.shop_name,
                                 ph.price,
                                 ph.currency,
                                 ph.is_available,
                                 ph.scraped_at, DATE (ph.scraped_at) as scrape_date
                          FROM price_history ph
                              JOIN product_links pl
                          ON ph.product_link_id = pl.id
                          WHERE pl.product_id = ?
                            AND ph.scraped_at >= datetime('now'
                              , '-' || ? || ' days')
                            AND ph.price IS NOT NULL
                          ORDER BY ph.scraped_at ASC
                          ''', (product_id, days)).fetchall()

    conn.close()

    if not rows:
        return {
            'labels': [],
            'datasets': [],
            'stats': {}
        }

    # Organiser les données par boutique
    shops_data = {}
    all_dates = set()

    for row in rows:
        shop = row['shop_name']
        date = row['scrape_date']
        price = float(row['price'])

        if shop not in shops_data:
            shops_data[shop] = {}

        # Garder le dernier prix du jour
        shops_data[shop][date] = price
        all_dates.add(date)

    # Créer les labels (dates triées)
    sorted_dates = sorted(all_dates)

    # Couleurs pour les boutiques
    colors = [
        'rgb(255, 99, 132)',  # Rouge
        'rgb(54, 162, 235)',  # Bleu
        'rgb(255, 205, 86)',  # Jaune
        'rgb(75, 192, 192)',  # Vert
        'rgb(153, 102, 255)',  # Violet
        'rgb(255, 159, 64)',  # Orange
    ]

    # Créer les datasets pour Chart.js
    datasets = []
    color_index = 0

    for shop, price_data in shops_data.items():
        # Créer la série de données pour cette boutique
        data_points = []
        for date in sorted_dates:
            if date in price_data:
                data_points.append(price_data[date])
            else:
                # Si pas de prix ce jour, garder le dernier prix connu
                data_points.append(data_points[-1] if data_points else None)

        datasets.append({
            'label': shop,
            'data': data_points,
            'borderColor': colors[color_index % len(colors)],
            'backgroundColor': colors[color_index % len(colors)].replace('rgb', 'rgba').replace(')', ', 0.1)'),
            'tension': 0.1,
            'fill': False
        })
        color_index += 1

    # Calculer les statistiques
    all_prices = [float(row['price']) for row in rows]
    stats = {
        'min_price': min(all_prices) if all_prices else 0,
        'max_price': max(all_prices) if all_prices else 0,
        'avg_price': sum(all_prices) / len(all_prices) if all_prices else 0,
        'total_records': len(rows),
        'shops_count': len(shops_data),
        'date_range': f"{sorted_dates[0]} à {sorted_dates[-1]}" if sorted_dates else "Aucune donnée"
    }

    return {
        'labels': sorted_dates,
        'datasets': datasets,
        'stats': stats
    }

def get_price_history_table(product_id, page=1, per_page=50, shop_filter=None):
    """
    Historique paginé pour tableau

    Args:
        product_id (int): ID du produit
        page (int): Page actuelle
        per_page (int): Éléments par page
        shop_filter (str): Filtrer par boutique

    Returns:
        dict: Données paginées + métadonnées
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Condition de filtre
    shop_condition = "AND pl.shop_name = ?" if shop_filter else ""
    params = [product_id]
    if shop_filter:
        params.append(shop_filter)

    # Compter le total
    total = cursor.execute(f'''
        SELECT COUNT(*)
        FROM price_history ph
        JOIN product_links pl ON ph.product_link_id = pl.id
        WHERE pl.product_id = ? {shop_condition}
    ''', params).fetchone()[0]

    # Récupérer les données paginées
    offset = (page - 1) * per_page
    params.extend([per_page, offset])

    rows = cursor.execute(f'''
        SELECT 
            ph.scraped_at,
            ph.price,
            ph.currency,
            ph.is_available,
            ph.error_message,
            pl.shop_name,
            pl.url
        FROM price_history ph
        JOIN product_links pl ON ph.product_link_id = pl.id
        WHERE pl.product_id = ? {shop_condition}
        ORDER BY ph.scraped_at DESC
        LIMIT ? OFFSET ?
    ''', params).fetchall()

    conn.close()

    return {
        'data': [dict_from_row(row) for row in rows],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page,
            'has_prev': page > 1,
            'has_next': page * per_page < total
        }
    }

def get_price_alerts_data(product_id):
    """
    Données pour les alertes de prix

    Returns:
        dict: Données d'alerte
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Prix actuel vs historique
    current_prices = cursor.execute('''
                                    SELECT pl.shop_name,
                                           ph.price,
                                           ph.scraped_at
                                    FROM price_history ph
                                             JOIN product_links pl ON ph.product_link_id = pl.id
                                    WHERE pl.product_id = ?
                                      AND ph.price IS NOT NULL
                                      AND ph.id IN (SELECT MAX(ph2.id)
                                                    FROM price_history ph2
                                                             JOIN product_links pl2 ON ph2.product_link_id = pl2.id
                                                    WHERE pl2.product_id = ?
                                                      AND ph2.price IS NOT NULL
                                                    GROUP BY pl2.shop_name)
                                    ''', (product_id, product_id)).fetchall()

    # Prix minimums historiques
    historical_mins = cursor.execute('''
                                     SELECT pl.shop_name,
                                            MIN(ph.price) as min_price,
                                            ph.scraped_at as min_price_date
                                     FROM price_history ph
                                              JOIN product_links pl ON ph.product_link_id = pl.id
                                     WHERE pl.product_id = ?
                                       AND ph.price IS NOT NULL
                                     GROUP BY pl.shop_name
                                     ''', (product_id,)).fetchall()

    conn.close()

    alerts = []
    current_dict = {row['shop_name']: row for row in current_prices}
    min_dict = {row['shop_name']: row for row in historical_mins}

    for shop in current_dict:
        current = current_dict[shop]
        historical_min = min_dict.get(shop)

        if historical_min:
            price_diff = current['price'] - historical_min['min_price']
            percentage_diff = (price_diff / historical_min['min_price']) * 100

            alert_data = {
                'shop_name': shop,
                'current_price': current['price'],
                'min_price': historical_min['min_price'],
                'difference': price_diff,
                'percentage': percentage_diff,
                'is_best_price': abs(percentage_diff) < 1,  # Moins de 1% de différence
                'alert_type': 'best_price' if abs(percentage_diff) < 1 else 'normal'
            }
            alerts.append(alert_data)

    return alerts

"""STATS"""
def get_global_stats():
    """Récupérer les statistiques globales de l'application"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Nombre d'articles suivis
        products_count = cursor.execute('SELECT COUNT(*) FROM products').fetchone()[0]

        # Nombre de liens suivis
        links_count = cursor.execute('SELECT COUNT(*) FROM product_links').fetchone()[0]

        # Nombre total de scraping
        total_scrapes = cursor.execute('SELECT COUNT(*) FROM price_history').fetchone()[0]

        # Nombre de scraping réussis
        successful_scrapes = cursor.execute('''
                                            SELECT COUNT(*)
                                            FROM price_history
                                            WHERE is_available = 1
                                              AND price IS NOT NULL
                                            ''').fetchone()[0]

        # Nombre de scraping échoués
        failed_scrapes = cursor.execute('''
                                        SELECT COUNT(*)
                                        FROM price_history
                                        WHERE scraped_at IS NOT NULL
                                          AND (is_available = 0 OR price IS NULL)
                                        ''').fetchone()[0]

        # Nombre de boutiques différentes
        unique_shops = cursor.execute('''
                                      SELECT COUNT(DISTINCT shop_name)
                                      FROM product_links
                                      ''').fetchone()[0]

        # Nombre de boutiques sans aucun scraping réussi
        shops_without_success = cursor.execute('''
                                               SELECT COUNT(DISTINCT pl.shop_name)
                                               FROM product_links pl
                                                        LEFT JOIN price_history ph ON pl.id = ph.product_link_id
                                                   AND ph.is_available = 1 AND ph.price IS NOT NULL
                                               WHERE ph.id IS NULL
                                               ''').fetchone()[0]

        conn.close()

        return {
            'products_count': products_count,
            'links_count': links_count,
            'total_scrapes': total_scrapes,
            'successful_scrapes': successful_scrapes,
            'failed_scrapes': failed_scrapes,
            'unique_shops': unique_shops,
            'shops_without_success': shops_without_success,
            'success_rate': round((successful_scrapes / total_scrapes * 100) if total_scrapes > 0 else 0, 1)
        }

    except Exception as e:
        logger.error(f"Erreur récupération statistiques globales: {e}")
        return {
            'products_count': 0,
            'links_count': 0,
            'total_scrapes': 0,
            'successful_scrapes': 0,
            'failed_scrapes': 0,
            'unique_shops': 0,
            'shops_without_success': 0,
            'success_rate': 0
        }

def get_scraping_stats(product_id):
    """Statistiques de scraping pour un produit"""
    conn = get_db_connection()
    cursor = conn.cursor()

    stats = cursor.execute('''
                           SELECT COUNT(*)                                                as total_scrapes,
                                  COUNT(CASE WHEN ph.is_available = 1 THEN 1 END)        as successful_scrapes,
                                  COUNT(CASE WHEN ph.error_message IS NOT NULL THEN 1 END) as errors,
                                  MAX(ph.scraped_at)                                      as last_scrape
                           FROM price_history ph
                                    JOIN product_links pl ON ph.product_link_id = pl.id
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

def get_price_statistics(product_id, days=30):
    """
    Statistiques détaillées des prix

    Returns:
        dict: Statistiques complètes
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    stats = cursor.execute('''
                           SELECT MIN(ph.price)                as min_price,
                                  MAX(ph.price)                as max_price,
                                  AVG(ph.price)                as avg_price,
                                  COUNT(ph.id)                 as total_scrapes,
                                  COUNT(DISTINCT pl.shop_name) as shops_count,
                                  MIN(ph.scraped_at)           as first_scrape,
                                  MAX(ph.scraped_at)           as last_scrape
                           FROM price_history ph
                                    JOIN product_links pl ON ph.product_link_id = pl.id
                           WHERE pl.product_id = ?
                             AND ph.price IS NOT NULL
                             AND ph.scraped_at >= datetime('now', '-' || ? || ' days')
                           ''', (product_id, days)).fetchone()

    # Meilleur prix actuel
    best_current = cursor.execute('''
                                  SELECT ph.price, pl.shop_name, ph.scraped_at
                                  FROM price_history ph
                                           JOIN product_links pl ON ph.product_link_id = pl.id
                                  WHERE pl.product_id = ?
                                    AND ph.price IS NOT NULL
                                    AND ph.is_available = 1
                                  ORDER BY ph.scraped_at DESC, ph.price ASC LIMIT 1
                                  ''', (product_id,)).fetchone()

    # Stats par boutique
    shop_stats = cursor.execute('''
                                SELECT pl.shop_name,
                                       COUNT(*)           as records_count,
                                       MIN(ph.price)      as min_price,
                                       MAX(ph.price)      as max_price,
                                       AVG(ph.price)      as avg_price,
                                       MAX(ph.scraped_at) as last_scrape
                                FROM price_history ph
                                         JOIN product_links pl ON ph.product_link_id = pl.id
                                WHERE pl.product_id = ?
                                  AND ph.price IS NOT NULL
                                GROUP BY pl.shop_name
                                ORDER BY avg_price ASC
                                ''', (product_id,)).fetchall()
    conn.close()

    if not stats or stats['total_scrapes'] == 0:
        return None

    return {
        'min_price': round(stats['min_price'], 2) if stats['min_price'] else 0,
        'max_price': round(stats['max_price'], 2) if stats['max_price'] else 0,
        'avg_price': round(stats['avg_price'], 2) if stats['avg_price'] else 0,

        'total_scrapes': stats['total_scrapes'],
        'shops_count': stats['shops_count'],
        'first_scrape': stats['first_scrape'],
        'last_scrape': stats['last_scrape'],

        'best_current': {
            'price': round(best_current['price'], 2) if best_current else 0,
            'shop': best_current['shop_name'] if best_current else 'Aucun',
            'date': best_current['scraped_at'] if best_current else None
        } if best_current else None,

        'by_shop': [dict_from_row(row) for row in shop_stats],
        'global': dict_from_row(stats) if stats else {}  # doublon, mais format de données brutes utilisé dans l'API
    }

def get_price_history_for_chart(product_id, days=30):
    """
    Données d'historique optimisées pour graphiques Chart.js

    Args:
        product_id (int): ID du produit
        days (int): Nombre de jours d'historique (7, 30, 90)

    Returns:
        dict: Données formatées pour Chart.js
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    rows = cursor.execute('''
        SELECT 
            ph.scraped_at,
            ph.price,
            ph.currency,
            ph.is_available,
            pl.shop_name
        FROM price_history ph
        JOIN product_links pl ON ph.product_link_id = pl.id
        WHERE pl.product_id = ? 
        AND ph.scraped_at >= datetime('now', '-{} days')
        AND ph.price IS NOT NULL
        ORDER BY ph.scraped_at ASC
    '''.format(days), (product_id,)).fetchall()

    conn.close()

    # Organiser par boutique
    shops_data = {}
    for row in rows:
        shop = row['shop_name']
        if shop not in shops_data:
            shops_data[shop] = {
                'label': shop,
                'data': [],
                'borderColor': utils.display_helpers._get_shop_color(shop),
                'backgroundColor': utils.display_helpers._get_shop_color(shop, alpha=0.1),
                'tension': 0.1
            }

        shops_data[shop]['data'].append({
            'x': row['scraped_at'][:16],  # Format YYYY-MM-DD HH:MM
            'y': float(row['price'])
        })

    return {
        'datasets': list(shops_data.values()),
        'currency': rows[0]['currency'] if rows else 'EUR'
    }

"""MISCELLANEOUS"""


