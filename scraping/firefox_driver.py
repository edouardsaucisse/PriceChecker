from selenium import webdriver
from selenium.webdriver.firefox.options import Options


def create_firefox_driver():
    options = Options()

    # User-Agent personnalisé
    options.set_preference("general.useragent.override",
                           "Mozilla/5.0 (X11; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0")

    # Autres options utiles pour le scraping
    options.set_preference("dom.webdriver.enabled", False)
    options.set_preference("useAutomationExtension", False)
    options.add_argument("--headless")  # Mode sans interface graphique

    driver = webdriver.Firefox(options=options)
    return driver
