import requests
import time

TOKEN = "8353241433:AAGvs4m6XHNYQHDm6_OXXJJjE-v77K_oa7U"
CHANNEL_ID = "-1002874650451"

# 1720336066 - Arseni Sorin Hodoroja
# 555720770 - Ciobanu Andrei
# 579913806 - Jumbei Olga

ALLOWED_USERS = [1720336066, 555720770, 579913806]

API_URL = f"https://api.telegram.org/bot{TOKEN}"


def get_username(user_id):
    try:
        r = requests.get(f"{API_URL}/getChat", params={"chat_id": user_id})
        data = r.json()
        if data.get("ok"):
            username = data["result"].get("username")
            first_name = data["result"].get("first_name")
            if username:
                return f"@{username}"
            return first_name or "Unknown"
        return "Unknown"
    except:
        return "Unknown"


def send_photo(file_id):
    requests.post(f"{API_URL}/sendPhoto", data={
        "chat_id": CHANNEL_ID,
        "photo": file_id
    })


def send_document(file_id):
    requests.post(f"{API_URL}/sendDocument", data={
        "chat_id": CHANNEL_ID,
        "document": file_id
    })


def send_video(file_id):
    requests.post(f"{API_URL}/sendVideo", data={
        "chat_id": CHANNEL_ID,
        "video": file_id
    })


def send_text(text):
    requests.post(f"{API_URL}/sendMessage", data={
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "HTML"
    })


def main():
    offset = 0

    while True:
        try:
            r = requests.get(f"{API_URL}/getUpdates", params={
                "offset": offset + 1,
                "timeout": 30
            })

            data = r.json()
            if not data.get("ok"):
                time.sleep(2)
                continue

            for update in data.get("result", []):
                offset = update["update_id"]

                message = update.get("message")
                if not message:
                    continue

                chat_type = message["chat"]["type"]
                user_id = message["from"]["id"]

                if chat_type != "private":
                    continue
                if user_id not in ALLOWED_USERS:
                    continue

                username = get_username(user_id)
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

                # FOTO
                if "photo" in message:
                    file_id = message["photo"][-1]["file_id"]
                    print(f"[{timestamp}] MESAJ DE LA {user_id} TIP: PHOTO ({username})")
                    send_photo(file_id)
                    continue

                # DOCUMENT
                if "document" in message:
                    file_id = message["document"]["file_id"]
                    file_name = message["document"].get("file_name", "")
                    print(f"[{timestamp}] MESAJ DE LA {user_id} TIP: DOCUMENT ({username}): {file_name}")
                    send_document(file_id)
                    continue

                # VIDEO
                if "video" in message:
                    file_id = message["video"]["file_id"]
                    print(f"[{timestamp}] MESAJ DE LA {user_id} TIP: VIDEO ({username})")
                    send_video(file_id)
                    continue

                # TEXT
                text = message.get("text")
                if text and not text.startswith("/"):
                    print(f"[{timestamp}] MESAJ DE LA {user_id} TIP: TEXT ({username}): {text}")
                    send_text(text)

        except Exception as e:
            print("Eroare:", e)
            time.sleep(3)


if __name__ == "__main__":
    main()
