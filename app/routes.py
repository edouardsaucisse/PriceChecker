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
Routes Flask pour PriceChecker
"""

import logging
import csv

from io import StringIO
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, make_response, current_app

from database.models import (
    add_product_link,
    create_product,
    delete_product,
    delete_product_link,
    get_all_products,
    get_db_connection,
    get_global_stats,
    get_latest_prices,
    get_price_statistics,
    get_price_history,
    get_price_history_for_chart,
    get_price_history_table,
    get_product_by_id,
    get_product_links,
    get_scraping_stats,
    record_price,
    scrape_all_product_links,
    update_product
)

from utils.validators import (
    validate_all_product_data,
    validate_all_link_data,
    validate_product_name,
    validate_shop_url,
)

logger = logging.getLogger(__name__)

main = Blueprint('main', __name__)

def handle_validation_errors(errors):
    """Helper pour afficher les erreurs de validation"""
    for error in errors:
        flash(error, 'error')

@main.route('/')
def index():
    try:
        products = get_all_products()  # Toujours récupérer les produits à jour
        global_stats = get_global_stats()  # Ajouter les statistiques globales
        return render_template('index.html', products=products, global_stats=global_stats)
    except Exception as e:
        logger.error(f"Erreur chargement produits: {e}")
        flash(f'Erreur lors du chargement: {e}', 'error')
        return render_template('index.html', products=[], global_stats={})

@main.route('/add_product', methods=['GET', 'POST'])
def add_product():
    """Ajouter un nouveau produit avec validation"""
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()

            # ✅ VALIDATION AVEC LES VALIDATEURS
            is_valid, errors = validate_all_product_data(name, description)

            if not is_valid:
                handle_validation_errors(errors)
                return render_template('add_product.html',
                                     name=name,
                                     description=description)

            # Créer le produit si validation OK
            product_id = create_product(name, description or None)
            logger.info(f"Produit créé: {name} (ID: {product_id})")
            flash(f'Produit "{name}" créé avec succès!', 'success')
            return redirect(url_for('main.product_detail', product_id=product_id))

        except Exception as e:
            logger.error(f"Erreur création produit: {e}")
            flash(f'Erreur lors de la création: {e}', 'error')

    return render_template('add_product.html')

@main.route('/product/<int:product_id>/add_link', methods=['GET', 'POST'])
def add_product_link_route(product_id):
    """Ajouter un lien de boutique à un produit"""
    # Vérifier que le produit existe
    product = get_product_by_id(product_id)
    if not product:
        flash('Produit non trouvé', 'error')
        return redirect(url_for('main.products'))

    if request.method == 'POST':
        try:
            shop_name = request.form.get('shop_name', '').strip()
            url = request.form.get('url', '').strip()
            css_selector = request.form.get('css_selector', '').strip() or None

            # ✅ VALIDATION AVEC LES VALIDATEURS
            is_valid, errors = validate_all_link_data(
                product_id, shop_name, url, css_selector
            )

            if not is_valid:
                handle_validation_errors(errors)
                return render_template('add_link.html',
                                     product=product,
                                     shop_name=shop_name,
                                     url=url,
                                     css_selector=css_selector)

            # Ajouter le lien si validation OK
            link_id = add_product_link(product_id, shop_name, url, css_selector)
            logger.info(f"Lien ajouté: {shop_name} pour produit {product_id}")
            flash(f'Lien "{shop_name}" ajouté avec succès!', 'success')
            return redirect(url_for('main.product_detail', product_id=product_id))

        except Exception as e:
            logger.error(f"Erreur ajout lien: {e}")
            flash(f'Erreur lors de l\'ajout: {e}', 'error')

    return render_template('add_link.html', product=product)

@main.route('/api/link/<int:link_id>/test-scraping', methods=['POST'])
def api_link_scraping(link_id):
    """Tester le scraping d'un lien sans enregistrer en base"""
    try:
        # Récupérer les infos du lien
        conn = get_db_connection()
        link = conn.execute('''
            SELECT pl.*, p.name as product_name
            FROM product_links pl
            JOIN products p ON pl.product_id = p.id
            WHERE pl.id = ?
        ''', (link_id,)).fetchone()
        conn.close()

        if not link:
            return jsonify({
                'success': False,
                'error': 'Lien non trouvé'
            }), 404

        # Importer et utiliser le scraper
        from scraping.price_scraper import create_price_scraper
        scraper = create_price_scraper()

        # Tester le scraping
        price_data = scraper.scrape_price(
            url=link['url'],
            css_selector=link['css_selector'],
            shop_name=link['shop_name']
        )

        # Répondre selon le résultat
        return jsonify({
            'success': True,
            'price_found': price_data['is_available'] and price_data['price'] is not None,
            'price': price_data['price'],
            'currency': price_data['currency'],
            'is_available': price_data['is_available'],
            'error': price_data['error_message'],
            'shop_name': link['shop_name']
        })

    except Exception as e:
        logger.error(f"Erreur test scraping lien {link_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main.route('/api/product/<int:product_id>/price-chart')
def api_price_chart(product_id):
    """API JSON pour données du graphique"""
    try:
        days = request.args.get('days', 30, type=int)

        # Valider les jours
        if days not in [7, 30, 90, 365]:
            days = 30

        chart_data = get_price_history_for_chart(product_id, days)

        return jsonify({
            'success': True,
            'data': chart_data
        })

    except Exception as e:
        logger.error(f"Erreur API graphique produit {product_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main.route('/api/product/<int:product_id>/price-stats')
def api_price_stats(product_id):
    """API pour statistiques dynamiques"""
    try:
        days = request.args.get('days', 30, type=int)
        stats = get_price_statistics(product_id, days)

        return jsonify({
            'success': True,
            'stats': stats
        })

    except Exception as e:
        logger.error(f"Erreur API stats produit {product_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main.route('/api/products', methods=['GET', 'POST'])
def api_products():
    """API JSON pour les produits"""
    if request.method == 'GET':
        try:
            products = get_all_products()
            return jsonify({
                'status': 'success',
                'count': len(products),
                'products': products
            })
        except Exception as e:
            logger.error(f"Erreur API produits: {e}")
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    elif request.method == 'POST':
        try:
            data = request.get_json()
            if not data:
                return jsonify({
                    'status': 'error',
                    'message': 'Données JSON requises'
                }), 400

            name = data.get('name', '').strip()
            description = data.get('description', '').strip() or None

            # ✅ VALIDATION API AVEC LES VALIDATEURS
            is_valid, errors = validate_all_product_data(name, description)

            if not is_valid:
                return jsonify({
                    'status': 'error',
                    'message': 'Données invalides',
                    'errors': errors
                }), 400

            # Créer le produit
            product_id = create_product(name, description)
            logger.info(f"Produit créé via API: {name} (ID: {product_id})")

            return jsonify({
                'status': 'success',
                'message': 'Produit créé avec succès',
                'product_id': product_id
            }), 201

        except Exception as e:
            logger.error(f"Erreur API création produit: {e}")
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

@main.route('/api/product/<int:product_id>')
def api_product_detail(product_id):
    """API JSON pour un produit spécifique"""
    try:
        product = get_product_by_id(product_id)
        if not product:
            return jsonify({
                'status': 'error',
                'message': 'Produit non trouvé'
            }), 404

        prices = get_latest_prices(product_id)
        return jsonify({
            'status': 'success',
            'product': product,
            'prices': prices
        })
    except Exception as e:
        logger.error(f"Erreur API produit {product_id}: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@main.route('/api/product/<int:product_id>/links')
def api_product_links(product_id):
    """API JSON pour récupérer les liens d'un produit"""
    try:
        product = get_product_by_id(product_id)
        if not product:
            return jsonify({
                'status': 'error',
                'message': 'Produit non trouvé'
            }), 404

        links = get_product_links(product_id)
        return jsonify({
            'status': 'success',
            'count': len(links),
            'links': links
        })
    except Exception as e:
        logger.error(f"Erreur API liens produit {product_id}: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@main.route('/api/scraping/status/<int:product_id>')
def api_scraping_status(product_id):
    """API pour récupérer le statut du scraping"""

    try:
        stats = get_scraping_stats(product_id)
        latest_prices = get_latest_prices(product_id)  # ← Utiliser votre fonction

        return jsonify({
            'success': True,
            'stats': stats,
            'latest_prices': [dict(price) for price in latest_prices]  # ← Nouveau nom
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main.route('/api/validate/product-name', methods=['POST'])
def api_validate_product_name():
    """API pour valider un nom de produit en temps réel"""
    try:
        data = request.get_json()
        name = data.get('name', '') if data else ''

        is_valid, error = validate_product_name(name)

        return jsonify({
            'valid': is_valid,
            'message': error if not is_valid else 'Nom valide'
        })
    except Exception as e:
        return jsonify({
            'valid': False,
            'message': 'Erreur de validation'
        }), 500

@main.route('/api/validate/url', methods=['POST'])
def api_validate_url():
    """API pour valider une URL en temps réel"""
    try:
        data = request.get_json()
        url = data.get('url', '') if data else ''

        is_valid, error = validate_shop_url(url)

        return jsonify({
            'valid': is_valid,
            'message': error if not is_valid else 'URL valide'
        })
    except Exception as e:
        return jsonify({
            'valid': False,
            'message': 'Erreur de validation'
        }), 500

@main.route('/product/<int:product_id>/delete_link/<int:link_id>', methods=['POST'])
def delete_link(product_id, link_id):
    """Supprimer un lien de boutique"""
    try:
        # Vérifier que le produit existe
        product = get_product_by_id(product_id)
        if not product:
            flash('Produit non trouvé', 'error')
            return redirect(url_for('main.products'))

        # Supprimer le lien
        success = delete_product_link(link_id)

        if success:
            flash('Lien supprimé avec succès !', 'success')
            logger.info(f"Lien {link_id} supprimé du produit {product_id}")
        else:
            flash('Lien non trouvé', 'error')

        return redirect(url_for('main.product_detail', product_id=product_id))

    except Exception as e:
        logger.error(f"Erreur suppression lien {link_id}: {e}")
        flash('Erreur lors de la suppression', 'error')
        return redirect(url_for('main.product_detail', product_id=product_id))

@main.route('/product/<int:product_id>/delete', methods=['POST'])
def delete_product_route(product_id):
    """Supprimer un produit et toutes ses données associées"""
    try:
        # Récupérer le nom du produit avant suppression
        product = get_product_by_id(product_id)
        if not product:
            flash('Produit introuvable.', 'error')
            return redirect(url_for('main.products'))

        product_name = product['name']

        # Supprimer le produit
        success = delete_product(product_id)

        if success:
            flash(f'Produit "{product_name}" supprimé avec succès.', 'success')
            logger.info(f"Produit supprimé via interface: {product_name} (ID: {product_id})")
        else:
            flash('Erreur: produit introuvable.', 'error')

        return redirect(url_for('main.products'))

    except Exception as e:
        logger.error(f"Erreur suppression produit {product_id}: {str(e)}")
        flash('Erreur lors de la suppression du produit.', 'error')
        return redirect(url_for('main.products'))

@main.route('/product/<int:product_id>/edit', methods=['GET', 'POST'])
def edit_product(product_id):
    """Modifier un produit existant"""

    if request.method == 'POST':
        # Traitement du formulaire
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()

        if not name:
            flash('Le nom du produit est obligatoire', 'error')
            return redirect(url_for('main.edit_product', product_id=product_id))

        try:
            success = update_product(product_id, name, description if description else None)

            if success:
                flash('Produit mis à jour avec succès !', 'success')
                return redirect(url_for('main.product_detail', product_id=product_id))
            else:
                flash('Produit introuvable', 'error')
                return redirect(url_for('main.index'))
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash('Erreur lors de la mise à jour du produit', 'error')
            print(f"Erreur modification produit {product_id}: {e}")

        return redirect(url_for('main.edit_product', product_id=product_id))

    # Affichage du formulaire (GET)
    product = get_product_by_id(product_id)
    if not product:
        flash('Produit introuvable', 'error')
        return redirect(url_for('main.index'))  # ← main. ajouté

    return render_template('edit_product.html', product=product)

@main.route('/product/<int:product_id>/link/<int:link_id>/edit', methods=['GET', 'POST'])
def edit_product_link(product_id, link_id):
    """Éditer un lien de produit"""
    try:
        # Vérifier que le produit existe
        product = get_product_by_id(product_id)
        if not product:
            flash('Produit non trouvé', 'error')
            return redirect(url_for('main.products'))

        # Récupérer le lien à éditer
        conn = get_db_connection()
        link = conn.execute('''
                            SELECT *
                            FROM product_links
                            WHERE id = ?
                              AND product_id = ?
                            ''', (link_id, product_id)).fetchone()

        if not link:
            conn.close()
            flash('Lien non trouvé', 'error')
            return redirect(url_for('main.product_detail', product_id=product_id))

        if request.method == 'POST':
            shop_name = request.form.get('shop_name', '').strip()
            url = request.form.get('url', '').strip()
            css_selector = request.form.get('css_selector', '').strip()

            # Validation
            errors = []
            if not shop_name:
                errors.append('Le nom de la boutique est requis')
            if not url:
                errors.append('L\'URL est requise')
            if not url.startswith(('http://', 'https://')):
                errors.append('L\'URL doit commencer par http:// ou https://')

            # Vérifier l'unicité du nom de boutique (sauf pour le lien actuel)
            existing = conn.execute('''
                                    SELECT id
                                    FROM product_links
                                    WHERE product_id = ?
                                      AND shop_name = ?
                                      AND id != ?
                                    ''', (product_id, shop_name, link_id)).fetchone()

            if existing:
                errors.append(f'Une boutique "{shop_name}" existe déjà pour ce produit')

            if errors:
                conn.close()
                for error in errors:
                    flash(error, 'error')
                return render_template('edit_product_link.html',
                                       product=product,
                                       link=link,
                                       form_data=request.form)

            # Mettre à jour le lien
            conn.execute('''
                         UPDATE product_links
                         SET shop_name    = ?,
                             url          = ?,
                             css_selector = ?,
                             updated_at   = CURRENT_TIMESTAMP
                         WHERE id = ?
                         ''', (shop_name, url, css_selector or None, link_id))

            conn.commit()
            conn.close()

            flash(f'Lien "{shop_name}" modifié avec succès', 'success')
            return redirect(url_for('main.product_detail', product_id=product_id))

        conn.close()
        return render_template('edit_product_link.html', product=product, link=link)

    except Exception as e:
        logger.error(f"Erreur édition lien {link_id}: {e}")
        flash(f'Erreur lors de l\'édition: {e}', 'error')
        return redirect(url_for('main.product_detail', product_id=product_id))

@main.route('/product/<int:product_id>/history/export')
def export_price_history(product_id):
    """Export de l'historique des prix en CSV"""
    try:
        # ✅ Vérifier que le produit existe avec votre fonction
        product = get_product_by_id(product_id)
        if not product:
            flash('Produit introuvable.', 'error')
            return redirect(url_for('main.products'))

        # ✅ Récupérer l'historique avec votre fonction
        price_history = get_price_history(product_id, limit=1000)  # Plus de données pour export

        if not price_history:
            flash('Aucune donnée à exporter pour ce produit.', 'warning')
            return redirect(url_for('main.price_history', product_id=product_id))

        # ✅ Créer le CSV en mémoire
        output = StringIO()
        writer = csv.writer(output, delimiter=';', quoting=csv.QUOTE_MINIMAL)

        # En-têtes CSV
        writer.writerow([
            'Date et heure',
            'Boutique',
            'Prix',
            'Devise',
            'Disponible',
            'URL',
            'Message d\'erreur'
        ])

        # ✅ Écrire les données (adaptées à vos dictionnaires)
        for record in price_history:
            writer.writerow([
                record.get('scraped_at', '').replace('T', ' ')[:19] if record.get('scraped_at') else '',
                record.get('shop_name', ''),
                f"{record['price']:.2f}" if record.get('price') is not None else '',
                record.get('currency', 'EUR'),
                'Oui' if record.get('is_available') else 'Non',
                record.get('url', ''),
                record.get('error_message', '')
            ])

        # ✅ Préparer le fichier pour téléchargement
        output.seek(0)

        # Nom de fichier sécurisé
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        product_name = product.get('name', 'produit').replace(' ', '_')
        # Nettoyer le nom pour éviter les caractères problématiques
        safe_name = "".join(c for c in product_name if c.isalnum() or c in ('_', '-')).rstrip()
        filename = f"historique_prix_{safe_name}_{timestamp}.csv"

        # ✅ Créer la réponse HTTP avec headers corrects
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'

        logger.info(f"Export CSV généré pour produit {product_id}: {len(price_history)} enregistrements")
        return response

    except Exception as e:
        logger.error(f"Erreur export CSV produit {product_id}: {str(e)}")
        import traceback
        traceback.print_exc()  # Debug complet
        flash('Erreur lors de l\'export CSV.', 'error')
        return redirect(url_for('main.price_history', product_id=product_id))

@main.route('/product/<int:product_id>/history')
def price_history(product_id):
    """Page d'historique des prix"""
    try:
        # Récupérer le produit
        product = get_product_by_id(product_id)
        if not product:
            flash('Produit introuvable', 'error')
            return redirect(url_for('main.products'))

        # Paramètres de filtre
        days = request.args.get('days', 30, type=int)
        page = request.args.get('page', 1, type=int)
        shop_filter = request.args.get('shop', None)

        # Statistiques
        stats = get_price_statistics(product_id, days)

        # Tableau d'historique paginé
        history_data = get_price_history_table(
            product_id,
            page=page,
            shop_filter=shop_filter
        )

        # Liste des boutiques pour le filtre
        links = get_product_links(product_id)
        shops = [link['shop_name'] for link in links]

        return render_template('price_history.html',
                             product=product,
                             stats=stats,
                             history_data=history_data,
                             shops=shops,
                             current_days=days,
                             current_shop=shop_filter,
                             current_page=page)

    except Exception as e:
        logger.error(f"Erreur page historique produit {product_id}: {e}")
        flash('Erreur lors du chargement de l\'historique', 'error')
        return redirect(url_for('main.product_detail', product_id=product_id))

@main.route('/product/<int:product_id>/history/chart-data')
def price_history_chart_data(product_id):
    """API pour les données du graphique"""
    try:

        days = request.args.get('days', 30, type=int)
        shop_filter = request.args.get('shop', None)

        chart_data = get_price_history_for_chart(product_id, days)

        # Filtrer par boutique si nécessaire
        if shop_filter and shop_filter != 'all':
            filtered_datasets = []
            for dataset in chart_data.get('datasets', []):
                if dataset.get('label') == shop_filter:
                    filtered_datasets.append(dataset)
            chart_data['datasets'] = filtered_datasets

        return jsonify(chart_data)

    except Exception as e:
        logger.error(f"Erreur données graphique produit {product_id}: {e}")
        return jsonify({'error': str(e)}), 500

@main.route('/products')
def products():
    """Liste tous les produits avec leurs informations de prix enrichies"""
    try:
        products = get_all_products()

        # 🎯 ENRICHIR CHAQUE PRODUIT AVEC SES DONNÉES DE PRIX
        for product in products:
            try:
                # Récupérer les données de prix pour ce produit
                price_data = get_latest_prices(product['id'])

                # Ajouter les informations directement au produit
                if price_data and 'best_price' in price_data:
                    product['best_price'] = price_data['best_price']
                else:
                    product['best_price'] = None

                # Compter les boutiques disponibles
                if price_data and 'prices' in price_data:
                    available_prices = [
                        p for p in price_data['prices']
                        if p['is_available'] and p['price'] is not None
                    ]
                    product['available_shops'] = len(available_prices)
                    product['has_prices'] = len(price_data['prices']) > 0

                    # Ajouter quelques prix récents pour l'affichage (optionnel)
                    product['recent_prices'] = available_prices[:3]
                else:
                    product['available_shops'] = 0
                    product['has_prices'] = False
                    product['recent_prices'] = []

            except Exception as e:
                logger.warning(f"Erreur récupération prix pour produit {product['id']}: {e}")
                # Valeurs par défaut en cas d'erreur
                product['best_price'] = None
                product['available_shops'] = 0
                product['has_prices'] = False
                product['recent_prices'] = []

        return render_template('products.html', products=products)

    except Exception as e:
        logger.error(f"Erreur lors du chargement des produits: {e}")
        flash('Erreur lors du chargement des produits', 'error')
        return render_template('products.html', products=[])

@main.route('/product/<int:product_id>')
def product_detail(product_id):
    """Détail d'un produit avec ses prix"""
    try:
        product = get_product_by_id(product_id)
        if not product:
            flash('Produit non trouvé', 'error')
            return redirect(url_for('main.products'))

        prices = get_latest_prices(product_id)
        links = get_product_links(product_id)

        stats = get_scraping_stats(product_id)
        latest_prices = get_latest_prices(product_id)

        return render_template('product_detail.html',
                             product=product,
                             prices=prices['prices'],
                             best_price=prices['best_price'],
                             links=links,
                             get_product_links=get_product_links,
                             stats=stats,
                             latest_prices=latest_prices)

    except Exception as e:
        logger.error(f"Erreur chargement produit {product_id}: {e}")
        flash(f'Erreur lors du chargement: {e}', 'error')
        return redirect(url_for('main.products'))

@main.route('/quick_scrape_product/<int:product_id>', methods=['POST'])
def products_single_scrape(product_id):
    """Scraper rapidement un produit et rediriger selon la source"""
    try:

        results = scrape_all_product_links(product_id)

        successful = [r for r in results if r.get('success', False)]
        failed = [r for r in results if not r.get('success', False)]

        if successful:
            flash(f'✅ Prix mis à jour avec succès ! {len(successful)} prix récupérés.', 'success')

        if failed:
            failed_shops = [r['shop_name'] for r in failed]
            flash(f'⚠️ Échec(s) pour: {", ".join(failed_shops)}', 'warning')

        if not results:
            flash('ℹ️ Aucun lien à scraper pour ce produit.', 'info')

        return redirect(url_for('main.products'))

    except Exception as e:
        logger.error(f"Erreur scraping produit {product_id}: {e}")
        flash(f'❌ Erreur lors du scraping: {str(e)}', 'error')
        return redirect(url_for('main.products'))

@main.route('/product/<int:product_id>/quick-scrape', methods=['POST'])
def quick_scrape_product(product_id):
    """Scraping rapide depuis la page produit"""

    try:
        product = get_product_by_id(product_id)
        if not product:
            flash('Produit non trouvé.', 'error')
            return redirect(url_for('main.products'))

        results = scrape_all_product_links(product_id)

        successful = [r for r in results if r.get('success', False)]
        failed = [r for r in results if not r.get('success', False)]

        if successful:
            flash(f'✅ Prix mis à jour ! {len(successful)} boutique(s) scrapée(s) avec succès.', 'success')

        if failed:
            failed_shops = [r['shop_name'] for r in failed]
            flash(f'⚠️ Échec(s) pour: {", ".join(failed_shops)}', 'warning')

        if not results:
            flash('ℹ️ Aucun lien à scraper pour ce produit.', 'info')

        return redirect(url_for('main.product_detail', product_id=product_id))

    except Exception as e:
        logger.error(f"Erreur scraping rapide produit {product_id}: {e}")
        flash(f'❌ Erreur lors du scraping: {str(e)}', 'error')
        return redirect(url_for('main.product_detail', product_id=product_id))

@main.route('/scrape-all', methods=['POST'])
def scrape_all_products():
    """Scraper tous les prix de tous les produits"""

    try:
        # Récupérer tous les produits qui ont des liens
        conn = get_db_connection()
        cursor = conn.cursor()

        products_with_links = cursor.execute('''
                                             SELECT DISTINCT p.id, p.name
                                             FROM products p
                                                      JOIN product_links pl ON p.id = pl.product_id
                                             ORDER BY p.name
                                             ''').fetchall()

        conn.close()

        if not products_with_links:
            flash('ℹ️ Aucun produit avec des liens à scraper.', 'info')
            return redirect(url_for('main.products'))

        # Statistiques
        total_products = len(products_with_links)
        total_successful = 0
        total_failed = 0
        products_processed = []

        # Scraper chaque produit
        for product in products_with_links:
            try:
                results = scrape_all_product_links(product['id'])

                successful = [r for r in results if r.get('success', False)]
                failed = [r for r in results if not r.get('success', False)]

                total_successful += len(successful)
                total_failed += len(failed)

                products_processed.append({
                    'name': product['name'],
                    'successful': len(successful),
                    'failed': len(failed)
                })

            except Exception as e:
                logger.error(f"Erreur scraping produit {product['id']}: {e}")
                total_failed += 1

        # Messages de résultats
        if total_successful > 0:
            flash(f'✅ Scraping global terminé ! {total_successful} prix récupérés sur {total_products} produit(s).',
                  'success')

        if total_failed > 0:
            flash(f'⚠️ {total_failed} échec(s) de scraping détectés.', 'warning')

        # Log détaillé optionnel
        logger.info(f"Scraping global: {total_products} produits, {total_successful} succès, {total_failed} échecs")

        return redirect(url_for('main.products'))

    except Exception as e:
        logger.error(f"Erreur scraping global: {e}")
        flash(f'❌ Erreur lors du scraping global: {str(e)}', 'error')
        return redirect(url_for('main.products'))

@main.route('/product/<int:product_id>/scrape/ajax', methods=['POST'])
def scrape_product_ajax(product_id):
    """Scraping AJAX pour un produit (non-bloquant)"""

    try:
        # Lancer le scraping en arrière-plan
        results = scrape_all_product_links(product_id)

        # Préparer la réponse JSON
        successful = [r for r in results if r.get('success', False)]
        failed = [r for r in results if not r.get('success', False)]

        return jsonify({
            'success': True,
            'total': len(results),
            'successful': len(successful),
            'failed': len(failed),
            'results': results,
            'message': f'Scraping terminé: {len(successful)} succès, {len(failed)} échecs'
        })

    except Exception as e:
        logger.error(f"Erreur scraping AJAX produit {product_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': f'Erreur: {str(e)}'
        }), 500

@main.app_template_filter('shop_color')
def shop_color_filter(shop_name, alpha=1.0):
    from utils.display_helpers import _get_shop_color
    return _get_shop_color(shop_name, alpha)