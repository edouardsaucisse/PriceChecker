from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def create_chrome_driver():
    options = Options()

    # User-Agent personnalisé
    options.add_argument(
        "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")

    # Options utiles pour le scraping
    options.add_argument("--headless")  # Mode sans interface graphique
    options.add_argument("--no-sandbox")  # Nécessaire sur certains systèmes Linux
    options.add_argument("--disable-dev-shm-usage")  # Évite les problèmes de mémoire partagée
    options.add_argument("--disable-blink-features=AutomationControlled")  # Évite la détection
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    # Créer le driver
    driver = webdriver.Chrome(options=options)

    # Masquer les propriétés webdriver
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    return driver