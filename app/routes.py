"""
Routes Flask pour PriceChecker
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app
import logging
from database.models import (
    get_all_products,
    create_product,
    get_product_by_id,
    add_product_link,
    get_latest_prices
)
# ✅ Import des validateurs
from utils.validators import (
    validate_all_product_data,
    validate_all_link_data,
    validate_product_name,
    validate_shop_url,
    validate_shop_name
)

# Configuration du logging
logger = logging.getLogger(__name__)

main = Blueprint('main', __name__)

def handle_validation_errors(errors):
    """Helper pour afficher les erreurs de validation"""
    for error in errors:
        flash(error, 'error')

@main.route('/')
def index():
    """Page d'accueil"""
    try:
        products = get_all_products()
        return render_template('index.html', products=products)
    except Exception as e:
        logger.error(f"Erreur chargement produits: {e}")
        flash(f'Erreur lors du chargement: {e}', 'error')
        return render_template('index.html', products=[])

@main.route('/products')
def products():
    """Liste des produits surveillés"""
    try:
        products = get_all_products()
        return render_template('products.html', products=products)
    except Exception as e:
        logger.error(f"Erreur chargement produits: {e}")
        flash(f'Erreur lors du chargement: {e}', 'error')
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
        return render_template('product_detail.html', product=product, prices=prices)
    except Exception as e:
        logger.error(f"Erreur chargement produit {product_id}: {e}")
        flash(f'Erreur lors du chargement: {e}', 'error')
        return redirect(url_for('main.products'))

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