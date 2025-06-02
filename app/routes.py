"""
Routes Flask pour PriceChecker
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
import sys
import os

# Ajouter le répertoire racine pour importer models
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from database.models import (
    get_all_products, 
    create_product, 
    get_product_by_id,
    add_product_link,
    get_latest_prices
)

main = Blueprint('main', __name__)


@main.route('/')
def index():
    """Page d'accueil"""
    try:
        products = get_all_products()
        return render_template('index.html', products=products)
    except Exception as e:
        flash(f'Erreur lors du chargement des produits: {e}', 'error')
        return render_template('index.html', products=[])


@main.route('/products')
def products():
    """Liste des produits surveillés"""
    try:
        products = get_all_products()
        return render_template('products.html', products=products)
    except Exception as e:
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
        flash(f'Erreur lors du chargement du produit: {e}', 'error')
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
            
            product_id = create_product(name, description)
            flash(f'Produit "{name}" créé avec succès!', 'success')
            return redirect(url_for('main.product_detail', product_id=product_id))
            
        except Exception as e:
            flash(f'Erreur lors de la création: {e}', 'error')
    
    return render_template('add_product.html')


@main.route('/api/products')
def api_products():
    """API JSON pour récupérer les produits"""
    try:
        products = get_all_products()
        return jsonify({
            'status': 'success',
            'products': [dict(product) for product in products]
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500