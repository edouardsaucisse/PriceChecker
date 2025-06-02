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

# Configuration du logging
logger = logging.getLogger(__name__)

main = Blueprint('main', __name__)

def handle_db_error(func):
    """Décorateur pour gérer les erreurs de base de données"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Erreur base de données dans {func.__name__}: {e}")
            flash(f'Erreur technique: {e}', 'error')
            return redirect(url_for('main.index'))
    return wrapper

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
    """Ajouter un nouveau produit"""
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()

            if not name:
                flash('Le nom du produit est obligatoire', 'error')
                return render_template('add_product.html')

            if len(name) < 3:
                flash('Le nom doit contenir au moins 3 caractères', 'error')
                return render_template('add_product.html')

            product_id = create_product(name, description)
            logger.info(f"Produit créé: {name} (ID: {product_id})")
            flash(f'Produit "{name}" créé avec succès!', 'success')
            return redirect(url_for('main.product_detail', product_id=product_id))

        except Exception as e:
            logger.error(f"Erreur création produit: {e}")
            flash(f'Erreur lors de la création: {e}', 'error')

    return render_template('add_product.html')

@main.route('/api/products')
def api_products():
    """API JSON pour récupérer les produits"""
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