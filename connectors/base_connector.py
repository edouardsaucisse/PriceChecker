from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urlparse
from config import Config

class BaseConnector(ABC):
    def __init__(self, url):
        self.url = url
        self.shop_name = self.get_shop_name()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    @abstractmethod
    def get_price(self):
        '''Retourne le prix du produit ou None si erreur'''
        pass
    
    @abstractmethod
    def get_shop_name(self):
        '''Retourne le nom de la boutique'''
        pass
    
    def make_request(self):
        '''Effectue la requête HTTP avec gestion d'erreurs'''
        try:
            response = self.session.get(
                self.url, 
                timeout=Config.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            raise Exception(f"Erreur de requête: {str(e)}")
    
    def parse_price(self, price_text):
        '''Parse le texte de prix pour extraire le nombre'''
        import re
        # Supprime les espaces et caractères non numériques sauf . et ,
        price_clean = re.sub(r'[^\d,.]', '', price_text.replace(' ', ''))
        # Remplace la virgule par un point pour les décimales
        price_clean = price_clean.replace(',', '.')
        try:
            return float(price_clean)
        except ValueError:
            return None
