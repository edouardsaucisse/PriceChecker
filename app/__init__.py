from flask import Flask

def create_app():
    app = Flask(__name__, 
                static_folder='../static',  # Chemin vers le dossier static
                static_url_path='/static')  # URL pour accéder aux fichiers statiques
    
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    
    # Importation et enregistrement des routes
    from app.routes import main
    app.register_blueprint(main)
    
    return app