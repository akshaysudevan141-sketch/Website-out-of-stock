import json
import os
import requests
from bs4 import BeautifulSoup

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
ALLOWED_CHAT_ID = str(os.environ.get("TELEGRAM_CHAT_ID"))
STATE_FILE = "watchlist.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"last_update_id": 0, "items": []}


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": ALLOWED_CHAT_ID,
        "text": text,
        "disable_web_page_preview": True
    }, timeout=15)


def process_telegram_commands(state):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    params = {"offset": state["last_update_id"] + 1, "timeout": 5}
    res = requests.get(url, params=params, timeout=15).json()

    if not res.get("ok"):
        return

    for update in res.get("result", []):
        state["last_update_id"] = max(state["last_update_id"], update["update_id"])
        msg = update.get("message", {})
        chat_id = str(msg.get("chat", {}).get("id", ""))
        text = msg.get("text", "").strip()

        # Ignore messages from anyone other than you
        if chat_id != ALLOWED_CHAT_ID or not text:
            continue

        if text.startswith("/add "):
            payload = text[5:].strip()
            if "|" not in payload:
                send_message("❌ Format: /add <URL> | <current keyword>\nExample:\n/add https://example.com/shoe | Out of Stock")
                continue

            target_url, keyword = [part.strip() for part in payload.split("|", 1)]
            state["items"].append({"url": target_url, "keyword": keyword})
            send_message(f"✅ Added to watchlist!\nURL: {target_url}\nWatching for change from: '{keyword}'")

        elif text == "/list":
            if not state["items"]:
                send_message("📭 Your watchlist is empty.\nUse: /add <URL> | <keyword>")
            else:
                lines = [f"{i+1}. {item['url']}\n   Keyword: '{item['keyword']}'" for i, item in enumerate(state["items"])]
                send_message("📋 Current Watchlist:\n\n" + "\n\n".join(lines))

        elif text.startswith("/remove "):
            try:
                idx = int(text.split()[1]) - 1
                removed = state["items"].pop(idx)
                send_message(f"🗑️ Removed: {removed['url']}")
            except (ValueError, IndexError):
                send_message("❌ Invalid number. Send /list to see item numbers.")

        elif text == "/help":
            send_message(
                "🤖 Commands:\n"
                "/add <URL> | <current keyword> - Track a page\n"
                "/list - Show active items\n"
                "/remove <number> - Stop tracking an item"
            )


def check_websites(state):
    remaining_items = []

    for item in state["items"]:
        url = item["url"]
        keyword = item["keyword"]
        try:
            res = requests.get(url, headers=HEADERS, timeout=20)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, "html.parser")
            page_text = soup.get_text(separator=" ").lower()

            if keyword.lower() not in page_text:
                send_message(
                    f"🚨 STATUS CHANGED!\n\n"
                    f"The keyword '{keyword}' is no longer on the page:\n{url}\n\n"
                    f"(Removed from watchlist. Send /add again if you want to keep tracking.)"
                )
            else:
                remaining_items.append(item)
        except Exception as e:
            print(f"Error checking {url}: {e}")
            remaining_items.append(item)

    state["items"] = remaining_items


if __name__ == "__main__":
    current_state = load_state()
    process_telegram_commands(current_state)
    check_websites(current_state)
    save_state(current_state)
