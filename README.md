# 🏷️ PriceChecker

**Application web de surveillance automatique des prix en ligne**

![Version](https://img.shields.io/badge/version-2.4.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.13%2B-green.svg)
![License](https://img.shields.io/badge/license-GPL--3.0-green.svg)


## 📋 **Description**

PriceChecker permet de surveiller automatiquement les prix de produits sur différents sites e-commerce. L'application scrape les prix, conserve un historique détaillé et offre une interface moderne pour gérer vos surveillances.

## ✨ **Fonctionnalités**

### 🎯 **Gestion des produits**
- ➕ Ajout de produits avec validation
- ✏️ Modification des informations
- 🗑️ Suppression sécurisée
- 🔗 Gestion multi-boutiques

### 📊 **Surveillance des prix**
- 🕷️ Web scraping automatisé (BeautifulSoup + Selenium)
- 📈 Historique complet des prix
- 📉 Graphiques interactifs (Chart.js)
- 📧 Export CSV des données

### 🎨 **Interface utilisateur**
- 📱 Design responsive (Bootstrap 5)
- 🎭 Icônes FontAwesome
- ⚡ Animations CSS fluides
- 🔄 Feedback temps réel

### 🔧 **API REST**
- 📥 Endpoints JSON complets
- 🧪 Tests automatisés
- 📋 Validation des données

### 🗃️ **Base de données**
- 🗂️ Initialisation automatique

## 🏗️ **Architecture technique**

```
├── 🌐 Frontend: HTML5, CSS3, JavaScript ES6
├── ⚙️ Backend: Flask 3.0, SQLite3
├── 🕷️ Scraping: BeautifulSoup4, Selenium
├── 📊 Charts: Chart.js, Moment.js
└── 🧪 Tests: pytest, coverage
```

## 🚀 **Installation**

### Prérequis
- Python 3.8+
- pip

### **Méthode rapide (Windows 🪟)**
Télécharger le projet puis exécuter les commandes suivantes :

```batch
# Installation automatique
install.bat

# Démarrage
start.bat
```

### **Installation manuelle (Windows 🪟, Linux 🐧, MacOS 🍏)**
```bash
# 1. Cloner le projet
git clone <repository-url>
cd PriceChecker

# 2. Créer l'environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate     # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. [OPTIONNEL] Initialiser la base de données
python -c "from database.models import init_db; init_db()"

# 5. Lancer l'application
python run.py
```

### **Accès à l'application**
🌐 Ouvrir : `http://localhost:5000`

## 📁 **Structure du projet**

```
PriceChecker/
├── 📂 app/                     # Application Flask
│   ├── 📂 templates/          # Templates Jinja2
│   ├── __init__.py            # Factory app
│   └── routes.py              # Routes & API
├── 📂 database/               # Base de données
│   └── models.py              # Modèles SQLite
├── 📂 scraping/               # Web scraping
│   ├── 📂 scrapers/           # Scrapers spécialisés
│   └── price_scraper.py       # Scraper principal
├── 📂 static/                 # Assets statiques
│   ├── 📂 css/               # Styles personnalisés
│   ├── 📂 js/                # JavaScript
│   └── 📂 images/            # Images & favicon
├── 📂 utils/                  # Utilitaires
│   ├── display_helpers.py     # Helpers templates
│   └── validators.py          # Validation données
├── 📂 tests/                  # Tests unitaires
├── 📂 logs/                   # Fichiers de logs
├── config.py                  # Configuration
├── run.py                     # Point d'entrée
└── requirements.txt           # Dépendances
```

## 🗃️ **Base de données**

### **Schéma SQLite :**
```sql
📋 products          # Produits surveillés
├── id (PK)
├── name             # Nom du produit
├── description      # Description
└── created_at       # Date création

🔗 product_links     # Liens boutiques
├── id (PK)
├── product_id (FK)
├── shop_name        # Nom boutique
├── url              # URL produit
├── css_selector     # Sélecteur prix
└── created_at

📊 price_history     # Historique prix
├── id (PK)
├── product_link_id (FK)
├── price            # Prix récupéré
├── currency         # Devise
├── is_available     # Disponibilité
├── error_message    # Erreur éventuelle
└── scraped_at       # Date scraping
```

## ⚙️ **Configuration**
Le fichier de configuration est `config.py`.

### **Variables d'environnement :**
```bash
# Application
SECRET_KEY=your-secret-key-here
DEBUG=False
HOST=0.0.0.0
PORT=5000

# Base de données
DATABASE_PATH=./pricechecker.db

# Scraping
SCRAPING_DELAY=2
MAX_RETRIES=3
TIMEOUT=30
USER_AGENT=PriceChecker/1.0
```

### **Configuration scraping :**
```python
# config.py
SCRAPING_CONFIG = {
    'delay_between_requests': 2,    # Délai entre requêtes (secondes)
    'timeout': 30,                  # Timeout requête (secondes)
    'max_retries': 3,              # Nombre de tentatives
    'user_agent': 'Custom Agent',   # User-Agent personnalisé
}
```

## 🧪 **Tests**

```bash
# Tests complets avec couverture
python -m pytest tests/ --cov=app --cov=database --cov-report=html

# Tests spécifiques
python -m pytest tests/test_models.py -v
python -m pytest tests/test_routes.py -v
python -m pytest tests/test_scraping.py -v

# Détection code mort
vulture . --exclude=.venv,.git,__pycache__
```

## 📊 **API Documentation**

### **Endpoints principaux :**
```http
# Produits
GET    /api/products              # Liste produits
POST   /api/products              # Créer produit
GET    /api/product/{id}          # Détail produit
GET    /api/product/{id}/links    # Liens produit

# Prix et historique
GET    /api/product/{id}/price-chart    # Données graphique
GET    /api/product/{id}/price-stats    # Statistiques
POST   /api/link/{id}/test-scraping     # Test scraping

# Validation
POST   /api/validate/product-name       # Valider nom
POST   /api/validate/url               # Valider URL
```

### **Exemple réponse API :**
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "name": "iPhone 15",
    "prices": [
      {
        "shop_name": "Apple",
        "price": 799.00,
        "currency": "EUR",
        "is_available": true,
        "scraped_at": "2024-01-15T10:30:00Z"
      }
    ]
  }
}
```

## 🛠️ **Développement**

### **Ajouter un scraper personnalisé :**
```python
# scraping/scrapers/nouveau_site.py
def scrape_nouveau_site(url, css_selector=None):
    """Scraper pour nouveau site"""
    # Votre logique ici
    return {
        'price': 29.99,
        'currency': 'EUR',
        'is_available': True,
        'error_message': None
    }
```

### **Commandes utiles :**
```bash
# Formatage du code
black app/ database/ utils/

# Linting
flake8 app/ database/ utils/

# Nettoyage base de données
python -c "from database.models import cleanup_old_prices; cleanup_old_prices()"
```

## 🐛 **Résolution de problèmes**

### **Erreurs courantes :**

| Erreur | Cause | Solution |
|--------|-------|----------|
| `Database locked` | SQLite en cours d'utilisation | Redémarrer l'app |
| `403 Forbidden` | User-Agent détecté | Changer USER_AGENT |
| `Template not found` | Chemin incorrect | Vérifier TEMPLATES_PATH |
| `Import Error` | Module manquant | `pip install -r requirements.txt` |

### **Logs et debugging :**
```bash
# Consulter les logs
tail -f logs/app.log

# Debug mode
export DEBUG=True
python run.py
```

## 🔮 **Roadmap v2.0**

### **Fonctionnalités à venir :**
- [ ] 🔐 Authentification multi-utilisateurs
- [ ] ✳️ Tags et catégories de produits
- [ ] 📧 Notifications email/Slack (seuil automatique ou paramétrable)
- [ ] 📈 Statistiques avancées
- [ ] 🌍 Support multi-langues
- [ ] 🔁 Import/export base de données
- [ ] 📦 Sauvegarde automatique (Google Drive, S3, etc.)
- [ ] 📊 Page "boutiques"
- [ ] 👑 Page d'administration
- [ ] 💰 Achat optimisé
- [ ] 🔎 Filtres
### **UX/UI :**
- [ ] 🖌️ Refonte de l'interface/Quality of Life
- [ ] 🎨 Nouveau thème sombre
- [ ] 📱 Application mobile (React Native)
### **Maintenance :**
- [ ] 🧹 Factorisation, Nettoyage code obsolète
- [ ] 🗑️ Nettoyage base de données
- [ ] 🔄 Mise à jour dépendances
- [ ] 📦 Mode Production
- [ ] 📦 Mode Développement (hot-reload, debug)
- [ ] 🧪 Implémentation de logs
- [ ] 🧪 Tests unitaires
### **Techniques :**
- [ ] 🔐 Implémentation de principes de sécurité (CSRF, XSS, etc.) 
- [ ] ❌ Gestion des erreurs
- [ ] 🐍 Migration vers Python 3.11
- [ ] 🤖 API webhooks
- [ ] 📦 Application autonome
- [ ] 🐳 Conteneurisation Docker
### **Documentation :**
- [ ] 📖 Documentation utilisateur/administrateur
- [ ] 📖 Documentation API
- [ ] 📚 Guide de contribution

## 📞 **Support et contribution**

- 🐛 **Issues** : [GitHub Issues](repository-url/issues)
- 📧 **Email** : N/A
- 📖 **Documentation** : [Wiki](repository-url/wiki)
- 💬 **Discussions** : [GitHub Discussions](repository-url/discussions)

## 🔒 Licence et droits d'auteur

### GNU General Public License v3.0

Ce logiciel est distribué sous la licence GNU GPL v3.0. 

**Cela signifie que :**
- ✅ Vous pouvez utiliser ce logiciel gratuitement
- ✅ Vous pouvez modifier le code source
- ✅ Vous pouvez redistribuer le logiciel
- ⚠️ **OBLIGATION** : Toute modification ou distribution doit inclure le code source
- ⚠️ **OBLIGATION** : Les œuvres dérivées doivent également être sous GPL v3.0
- ⛔ **INTERDICTION** : Utilisation dans des logiciels propriétaires fermés

### Copyright
- ~~Copyright (C) 2024 PriceChecker Project~~
- Ce programme est un logiciel libre : vous pouvez le redistribuer et/ou le modifier selon les termes de la Licence Publique Générale GNU telle que publiée par la Free Software Foundation, soit la version 3 de la Licence, ou (à votre option) toute version ultérieure.
- Ce programme est distribué dans l'espoir qu'il sera utile, mais SANS AUCUNE GARANTIE ; sans même la garantie implicite de COMMERCIALISATION ou d'ADÉQUATION À UN USAGE PARTICULIER. Voir la Licence Publique Générale GNU pour plus de détails.

**Texte complet de la licence :** [LICENSE](LICENSE) | [GNU GPL v3.0](https://www.gnu.org/licenses/gpl-3.0.html)

---

**Développé avec ❤️ en Python & Flask**
