# 🏷️ PriceChecker

**Application Flask de surveillance automatique des prix en ligne**

## 📋 Description

PriceChecker est une application web qui permet de surveiller automatiquement les prix de produits sur différents sites e-commerce. Elle scrape les prix, conserve un historique et envoie des alertes lorsque les prix changent.

## ✨ Fonctionnalités

- 📦 **Gestion des produits** - Ajout, modification, suppression
- 🔗 **Multi-boutiques** - Surveillance sur plusieurs sites
- 📊 **Historique des prix** - Conservation des données sur 30 jours
- 🕷️ **Web scraping** - Récupération automatique des prix
- 📧 **Alertes** - Notifications par email
- 📱 **Interface responsive** - Compatible mobile/desktop
- 🔄 **API REST** - Accès aux données en JSON

## 🏗️ Stack technique
- **Backend** : Flask, SQLAlchemy
- **Base de données** : SQLite
- **Frontend** : HTML, CSS, JavaScript (Materialize CSS)
- **Web scraping** : BeautifulSoup, Requests
- **Tests** : pytest
- **Déploiement** : Docker, manuel

## 🚀 Installation

### Prérequis
- Python 3.8+
- pip

### Installation rapide
```bash
# Cloner le projet
git clone <url-du-repo>
cd PriceChecker

# Installer les dépendances
pip install -r requirements.txt

# Initialiser la base de données
python -c "from database.models import init_db; init_db()"

# Lancer l'application
python run.py
```

### Installation Windows (batch)
```bash
# Installation automatique
install.bat

# Démarrage
start.bat
```

## 📁 Structure du projet

```
PriceChecker/
├── 📁 app/                    # Application Flask
│   ├── __init__.py           # Factory de l'app
│   ├── routes.py             # Routes et vues
│   └── 📁 templates/         # Templates HTML
├── 📁 database/              # Base de données
│   └── models.py             # Modèles SQLite
├── 📁 static/                # Fichiers statiques
│   ├── 📁 css/              # Styles CSS
│   ├── 📁 js/               # JavaScript
│   └── 📁 images/           # Images et favicon
├── 📁 connectors/            # Connecteurs web scraping
├── 📁 utils/                 # Utilitaires
├── 📁 tests/                 # Tests unitaires
├── 📁 config/                # Configuration
├── config.py                 # Configuration principale
├── run.py                    # Point d'entrée
└── requirements.txt          # Dépendances
```

## 🗃️ Base de données

### Tables principales :
- **`products`** - Produits surveillés
- **`product_links`** - Liens vers les boutiques
- **`price_history`** - Historique des prix

## ⚙️ Configuration

Modifiez `config.py` pour :
- Délais entre requêtes
- User-Agent du scraper
- Planification automatique
- Durée de l'historique

## 🧪 Tests

```bash
# Lancer les tests
python -m pytest tests/

# Avec couverture
python -m pytest tests/ --cov=app --cov=database
```

## 📊 API

### Endpoints disponibles :
- `GET /` - Page d'accueil
- `GET /products` - Liste des produits
- `GET /product/<id>` - Détail d'un produit
- `POST /add_product` - Ajouter un produit
- `GET /api/products` - API JSON des produits

## 🛠️ Développement

### Ajouter un nouveau connecteur :
1. Créer un fichier dans `connectors/`
2. Implémenter la fonction `scrape_price(url)`
3. Gérer les erreurs et timeouts

### Variables d'environnement :
```bash
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_PATH=/path/to/database
```

## 📈 Roadmap

- [x] ✅ Interface web de base
- [x] ✅ Gestion des produits
- [x] ✅ Base de données SQLite
- [ ] 🕷️ Web scraping automatique
- [ ] 📧 Système de notifications
- [ ] 📊 Graphiques des prix
- [ ] 🔐 Authentification utilisateurs

## 🐛 Résolution de problèmes

### Erreurs courantes :
- **Base de données verrouillée** : Redémarrer l'application
- **Scraping bloqué** : Vérifier le User-Agent
- **Templates non trouvés** : Vérifier le chemin des templates

## 📞 Support

Pour les bugs et suggestions :
- Créer une issue sur GitHub
- Consulter les logs dans `logs/`

## 📄 Licence

MIT License - Voir LICENSE pour les détails.
