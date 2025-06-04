"""
Module de scraping des prix pour PriceChecker
"""

import re
import time
import logging
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from fake_useragent import UserAgent

logger = logging.getLogger(__name__)

class PriceScraper:
    """Classe principale pour le scraping des prix"""

    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

    def scrape_price(self, url: str, css_selector: Optional[str] = None, shop_name: str = "") -> Dict[str, Any]:
        """
        Scraper le prix d'une URL donnée

        Args:
            url: URL à scraper
            css_selector: Sélecteur CSS spécifique pour le prix
            shop_name: Nom de la boutique (pour logs)

        Returns:
            Dict contenant price, currency, is_available, error_message
        """
        logger.info(f"🔍 Scraping prix pour {shop_name}: {url}")

        try:
            # Essayer d'abord avec requests (plus rapide)
            result = self._scrape_with_requests(url, css_selector, shop_name)

            # Si échec, essayer avec Selenium pour contenu dynamique
            if not result['is_available'] and not result['price']:
                logger.info(f"Tentative avec Selenium pour {shop_name}")
                result = self._scrape_with_selenium(url, css_selector, shop_name)

            return result

        except Exception as e:
            logger.error(f"Erreur scraping {shop_name}: {e}")
            return {
                'price': None,
                'currency': 'EUR',
                'is_available': False,
                'error_message': f'Erreur de scraping: {str(e)}'
            }

    def _scrape_with_requests(self, url: str, css_selector: Optional[str], shop_name: str) -> Dict[str, Any]:
        """Scraping avec requests + BeautifulSoup"""
        try:
            # Rotation du User-Agent
            self.session.headers['User-Agent'] = self.ua.random

            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extraire le prix
            price_info = self._extract_price_from_soup(soup, css_selector, shop_name)

            if price_info['price']:
                logger.info(f"✅ Prix trouvé avec requests: {price_info['price']} {price_info['currency']}")
                return {
                    **price_info,
                    'is_available': True,
                    'error_message': None
                }
            else:
                return {
                    **price_info,
                    'is_available': False,
                    'error_message': 'Prix non trouvé avec requests'
                }

        except requests.RequestException as e:
            logger.warning(f"Erreur requests pour {shop_name}: {e}")
            return {
                'price': None,
                'currency': 'EUR',
                'is_available': False,
                'error_message': f'Erreur réseau: {str(e)}'
            }

    def _scrape_with_selenium(self, url: str, css_selector: Optional[str], shop_name: str) -> Dict[str, Any]:
        """Scraping avec Selenium pour contenu dynamique"""
        driver = None
        try:
            # Configuration Chrome headless
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument(f'--user-agent={self.ua.random}')

            driver = webdriver.Chrome(options=options)
            driver.set_page_load_timeout(15)

            driver.get(url)

            # Attendre un peu pour le chargement dynamique
            time.sleep(2)

            # Extraire le prix
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            price_info = self._extract_price_from_soup(soup, css_selector, shop_name)

            if price_info['price']:
                logger.info(f"✅ Prix trouvé avec Selenium: {price_info['price']} {price_info['currency']}")
                return {
                    **price_info,
                    'is_available': True,
                    'error_message': None
                }
            else:
                return {
                    **price_info,
                    'is_available': False,
                    'error_message': 'Prix non trouvé avec Selenium'
                }

        except (TimeoutException, WebDriverException) as e:
            logger.warning(f"Erreur Selenium pour {shop_name}: {e}")
            return {
                'price': None,
                'currency': 'EUR',
                'is_available': False,
                'error_message': f'Erreur navigateur: {str(e)}'
            }
        finally:
            if driver:
                driver.quit()

    def _extract_price_from_soup(self, soup: BeautifulSoup, css_selector: Optional[str], shop_name: str) -> Dict[str, Any]:
        """Extraire le prix depuis BeautifulSoup"""

        # Si sélecteur CSS fourni, l'utiliser en priorité
        if css_selector:
            return self._extract_with_css_selector(soup, css_selector, shop_name)

        # Sinon, essayer l'auto-détection
        return self._auto_detect_price(soup, shop_name)

    def _extract_with_css_selector(self, soup: BeautifulSoup, css_selector: str, shop_name: str) -> Dict[str, Any]:
        """Extraire avec sélecteur CSS spécifique"""
        try:
            elements = soup.select(css_selector)

            for element in elements:
                price_text = element.get_text(strip=True)
                price, currency = self._parse_price_text(price_text)

                if price:
                    logger.info(f"Prix trouvé avec CSS '{css_selector}': {price_text}")
                    return {'price': price, 'currency': currency}

            logger.warning(f"Aucun prix trouvé avec CSS '{css_selector}' pour {shop_name}")
            return {'price': None, 'currency': 'EUR'}

        except Exception as e:
            logger.error(f"Erreur CSS selector '{css_selector}': {e}")
            return {'price': None, 'currency': 'EUR'}

    def _auto_detect_price(self, soup: BeautifulSoup, shop_name: str) -> Dict[str, Any]:
        """Auto-détection du prix avec patterns communs"""

        # Sélecteurs CSS communs pour les prix
        common_selectors = [
            '.price', '.product-price', '.price-current', '.price-value',
            '#price', '#product-price', '.price-box .price',
            '[class*="price"]', '[id*="price"]', '.cost', '.amount',
            '.price-display', '.current-price', '.sale-price'
        ]

        # Essayer chaque sélecteur
        for selector in common_selectors:
            try:
                elements = soup.select(selector)
                for element in elements:
                    price_text = element.get_text(strip=True)
                    price, currency = self._parse_price_text(price_text)

                    if price:
                        logger.info(f"Prix auto-détecté avec '{selector}': {price_text}")
                        return {'price': price, 'currency': currency}
            except:
                continue

        # Dernière chance: recherche par regex dans tout le HTML
        return self._regex_price_search(soup, shop_name)

    def _regex_price_search(self, soup: BeautifulSoup, shop_name: str) -> Dict[str, Any]:
        """Recherche de prix par expressions régulières"""

        text_content = soup.get_text()

        # Patterns pour différents formats de prix
        price_patterns = [
            r'(\d{1,4}(?:[,\s]\d{3})*(?:[.,]\d{2})?)\s*€',  # Prix en euros
            r'€\s*(\d{1,4}(?:[,\s]\d{3})*(?:[.,]\d{2})?)',  # Euros devant
            r'(\d{1,4}(?:[,\s]\d{3})*(?:[.,]\d{2})?)\s*EUR',  # EUR
            r'(\d{1,4}(?:[,\s]\d{3})*(?:[.,]\d{2})?)\s*\$',   # Dollars
            r'\$\s*(\d{1,4}(?:[,\s]\d{3})*(?:[.,]\d{2})?)',   # Dollars devant
        ]

        for pattern in price_patterns:
            matches = re.findall(pattern, text_content)
            if matches:
                for match in matches:
                    price, currency = self._parse_price_text(match)
                    if price and price > 0.01:  # Prix minimum raisonnable
                        logger.info(f"Prix trouvé par regex: {match}")
                        return {'price': price, 'currency': currency}

        logger.warning(f"Aucun prix détecté pour {shop_name}")
        return {'price': None, 'currency': 'EUR'}

    def _parse_price_text(self, price_text: str) -> Tuple[Optional[float], str]:
        """Parser un texte pour extraire prix et devise"""
        if not price_text:
            return None, 'EUR'

        # Nettoyer le texte
        cleaned = re.sub(r'[^\d,.\s€$£¥]', '', price_text)

        # Déterminer la devise
        currency = 'EUR'
        if '$' in price_text:
            currency = 'USD'
        elif '£' in price_text:
            currency = 'GBP'
        elif '¥' in price_text:
            currency = 'JPY'

        # Extraire le nombre
        price_match = re.search(r'(\d{1,4}(?:[,\s]\d{3})*(?:[.,]\d{2})?)', cleaned)
        if price_match:
            price_str = price_match.group(1)

            # Normaliser le format (remplacer , par . pour les décimales)
            if ',' in price_str and '.' in price_str:
                # Format 1,234.56
                price_str = price_str.replace(',', '')
            elif ',' in price_str:
                # Vérifier si c'est des milliers ou des décimales
                parts = price_str.split(',')
                if len(parts) == 2 and len(parts[1]) == 2:
                    # Décimales (123,45)
                    price_str = price_str.replace(',', '.')
                else:
                    # Milliers (1,234)
                    price_str = price_str.replace(',', '')

            # Supprimer les espaces
            price_str = price_str.replace(' ', '')

            try:
                price = float(price_str)
                return price, currency
            except ValueError:
                pass

        return None, currency

# Fonction utilitaire pour l'export
def create_price_scraper() -> PriceScraper:
    """Factory function pour créer un scraper"""
    return PriceScraper()