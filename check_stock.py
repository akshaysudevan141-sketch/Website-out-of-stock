import time
import requests

TOKEN = "9146121146:AAHvPIfepeNTa_U_NSwgsSEd7CIoWXDKJow"
URL = f"https://api.telegram.org/bot{TOKEN}/"

def check_updates():
    offset = None
    print("Bot is running 24/7 and listening for commands...")
    while True:
        try:
            response = requests.get(f"{URL}getUpdates", params={"offset": offset, "timeout": 30})
            data = response.json()
            if "result" in data:
                for update in data["result"]:
                    offset = update["update_id"] + 1
                    handle_message(update)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

def handle_message(update):
    # Your logic for processing /add, /list, /remove, and checking stock goes here
    message = update.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "")
    
    if text.startswith("/add"):
        # Add item logic
        pass
    # Add your other command handlers...

if __name__ == "__main__":
    check_updates()
