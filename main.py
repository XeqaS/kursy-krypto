import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.by import By
from webdriver_manager.firefox import GeckoDriverManager
from tqdm import tqdm
from dotenv import load_dotenv

# Ładowanie zmiennych środowiskowych z pliku .env
load_dotenv()

def get_exchange_rates(urls):
    # Używanie webdriver-manager do zarządzania sterownikami
    service = FirefoxService(GeckoDriverManager().install())
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')
    
    driver = webdriver.Firefox(service=service, options=options)
    
    rates = {}
    for currency, url in tqdm(urls.items(), desc="Fetching exchange rates"):
        driver.get(url)
        time.sleep(3)  # Poczekaj, aż strona się załaduje
        
        try:
            price_element = driver.find_element(By.CLASS_NAME, 'zonda-individual-coin-info__value')
            price = price_element.text.strip()
            rates[currency] = price
        except Exception as e:
            print(f"Error retrieving {currency} rate: {e}")
            rates[currency] = None
    
    driver.quit()
    return rates

def send_to_discord(webhook_url, message):
    data = {
        "content": message
    }
    response = requests.post(webhook_url, json=data)
    return response.status_code

def main():
    urls = {
        'Solana': 'https://zondacrypto.com/pl/kurs-walut/kurs-solana-pln',
        'Ethereum': 'https://zondacrypto.com/pl/kurs-walut/kurs-ethereum-pln',
        'Bitcoin': 'https://zondacrypto.com/pl/kurs-walut/kurs-bitcoin-pln'
    }
    
    webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
    if not webhook_url:
        print("Error: DISCORD_WEBHOOK_URL is not set.")
        return
    
    rates = get_exchange_rates(urls)
    message = "\n".join([f"Kurs {currency} to {rate}" for currency, rate in rates.items() if rate])
    
    if message:
        status_code = send_to_discord(webhook_url, message)
        if status_code == 204:
            print("Successfully sent rates to Discord")
        else:
            print("Failed to send rates to Discord")
    else:
        print("No rates retrieved")

if __name__ == "__main__":
    main()
