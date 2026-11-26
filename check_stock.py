import os
import requests
from bs4 import BeautifulSoup

# Configuration from GitHub Secrets
URL = os.environ.get("TARGET_URL")
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Words that indicate the item is NOT available (case-insensitive)
OUT_OF_STOCK_PHRASES = [
    "out of stock",
    "sold out",
    "currently unavailable",
    "notify me",
    "coming soon"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

def send_telegram_alert(message):
    api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(api_url, json=payload)
    response.raise_for_status()

def check_availability():
    if not all([URL, BOT_TOKEN, CHAT_ID]):
        raise ValueError("Missing one or more required environment variables.")

    response = requests.get(URL, headers=HEADERS, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    page_text = soup.get_text(separator=" ").lower()

    is_out_of_stock = any(phrase in page_text for phrase in OUT_OF_STOCK_PHRASES)

    if not is_out_of_stock:
        print("Item appears to be IN STOCK! Sending Telegram alert...")
        send_telegram_alert(f"🚨 *IN STOCK ALERT!*\n\nYour item is available now:\n{URL}")
    else:
        print("Still out of stock.")

if __name__ == "__main__":
    check_availability()
  
