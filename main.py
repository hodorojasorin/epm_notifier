import requests
import time

TOKEN = "8353241433:AAGvs4m6XHNYQHDm6_OXXJJjE-v77K_oa7U"
CHANNEL_ID = "-1002874650451"

# 1720336066 - Arseni Sorin Hodoroja
# 555720770 - Ciobanu Andrei
# 579913806 - Jumbei Olga

ALLOWED_USERS = [1720336066, 555720770, 579913806]

API_URL = f"https://api.telegram.org/bot{TOKEN}"

last_reminder_date = None  # pentru a nu trimite reminderul de mai multe ori în aceeași zi
message_map = {}  # (user_chat_id, user_message_id) -> channel_message_id (pentru TEXT)


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


def send_confirmation(user_id, tip):
    text = f"Mesajul tău de tip {tip} a fost trimis pe chat-ul general al <b>Echipei de Producție Multimedia</b>."
    requests.post(f"{API_URL}/sendMessage", data={
        "chat_id": user_id,
        "text": text,
        "parse_mode": "HTML"
    })


def send_text(text):
    # trimite text simplu pe canal (folosit și de reminder și de prefix sticker)
    requests.post(f"{API_URL}/sendMessage", data={
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "HTML"
    })


def send_text_from_user(user_chat_id, user_message_id, text):
    """
    Trimite text pe canal și salvează maparea dintre mesajul din privat și cel din canal,
    ca să putem edita ulterior și pe canal când userul dă edit în privat.
    """
    r = requests.post(f"{API_URL}/sendMessage", data={
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "HTML"
    })

    data = r.json()
    if data.get("ok"):
        channel_msg_id = data["result"]["message_id"]
        key = (user_chat_id, user_message_id)
        message_map[key] = channel_msg_id


def send_photo(file_id, caption=None):
    data = {
        "chat_id": CHANNEL_ID,
        "photo": file_id
    }
    if caption:
        data["caption"] = caption
        data["parse_mode"] = "HTML"
    requests.post(f"{API_URL}/sendPhoto", data=data)


def send_document(file_id, caption=None):
    data = {
        "chat_id": CHANNEL_ID,
        "document": file_id
    }
    if caption:
        data["caption"] = caption
        data["parse_mode"] = "HTML"
    requests.post(f"{API_URL}/sendDocument", data=data)


def send_video(file_id, caption=None):
    data = {
        "chat_id": CHANNEL_ID,
        "video": file_id
    }
    if caption:
        data["caption"] = caption
        data["parse_mode"] = "HTML"
    requests.post(f"{API_URL}/sendVideo", data=data)


def send_sticker(file_id):
    requests.post(f"{API_URL}/sendSticker", data={
        "chat_id": CHANNEL_ID,
        "sticker": file_id
    })


def send_animation(file_id, caption=None):
    data = {
        "chat_id": CHANNEL_ID,
        "animation": file_id
    }
    if caption:
        data["caption"] = caption
        data["parse_mode"] = "HTML"
    requests.post(f"{API_URL}/sendAnimation", data=data)


def check_scheduled_reminders():
    global last_reminder_date

    now = time.localtime()
    current_date = time.strftime("%Y-%m-%d", now)

    # tm_wday: 0 = luni, 6 = duminică
    # REMINDER: marti la 14:10 (exemplu din codul tău)
    if now.tm_wday == 1 and now.tm_hour == 14 and now.tm_min == 10:
        if last_reminder_date != current_date:
            text = (
                "<b>Reminder automat:</b> astăzi, de la ora 15:00, are loc filmarea în sala de conferințe.\n"
                "Reacționați la acest mesaj cei care vin."
            )
            send_text(text)
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S', now)}] REMINDER TRIMIS PE CANAL")
            last_reminder_date = current_date


def handle_new_message(message):
    chat_type = message["chat"]["type"]
    user_id = message["from"]["id"]

    if chat_type != "private":
        return
    if user_id not in ALLOWED_USERS:
        return

    username = get_username(user_id)
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    prefix = "<b>Mesaj din partea Administrației:</b>"

    user_chat_id = message["chat"]["id"]
    user_msg_id = message["message_id"]

    # STICKER
    if "sticker" in message:
        file_id = message["sticker"]["file_id"]
        print(f"[{timestamp}] MESAJ DE LA {user_id} TIP: STICKER ({username})")
        send_text(prefix)
        send_sticker(file_id)
        send_confirmation(user_id, "sticker")
        return

    # GIF / ANIMATION
    if "animation" in message:
        file_id = message["animation"]["file_id"]
        print(f"[{timestamp}] MESAJ DE LA {user_id} TIP: GIF ({username})")
        send_animation(file_id, caption=prefix)
        send_confirmation(user_id, "GIF")
        return

    # FOTO
    if "photo" in message:
        file_id = message["photo"][-1]["file_id"]
        print(f"[{timestamp}] MESAJ DE LA {user_id} TIP: PHOTO ({username})")
        send_photo(file_id, caption=prefix)
        send_confirmation(user_id, "fotografie")
        return

    # DOCUMENT
    if "document" in message:
        file_id = message["document"]["file_id"]
        file_name = message["document"].get("file_name", "")
        print(f"[{timestamp}] MESAJ DE LA {user_id} TIP: DOCUMENT ({username}): {file_name}")
        send_document(file_id, caption=prefix)
        send_confirmation(user_id, "document")
        return

    # VIDEO
    if "video" in message:
        file_id = message["video"]["file_id"]
        print(f"[{timestamp}] MESAJ DE LA {user_id} TIP: VIDEO ({username})")
        send_video(file_id, caption=prefix)
        send_confirmation(user_id, "video")
        return

    # TEXT
    text = message.get("text")
    if text and not text.startswith("/"):
        print(f"[{timestamp}] MESAJ DE LA {user_id} TIP: TEXT ({username}): {text}")
        channel_text = f"{prefix}\n{text}"
        # aici trimitem PE CANAL și salvăm maparea pentru edit
        send_text_from_user(user_chat_id, user_msg_id, channel_text)
        send_confirmation(user_id, "text")


def handle_edited_message(edited):
    """
    Sincronizează edit-ul pentru TEXT:
    - user editează mesajul în privat
    - bot editează mesajul corespunzător de pe canal (dacă există mapare).
    """
    chat_type = edited["chat"]["type"]
    user_id = edited["from"]["id"]
    user_chat_id = edited["chat"]["id"]
    user_msg_id = edited["message_id"]

    if chat_type != "private":
        return
    if user_id not in ALLOWED_USERS:
        requests.post(f"{API_URL}/sendMessage", data={
        "chat_id": user_id,
        "text": "Nu ai acces la acest bot.",
    })
        return

    new_text = edited.get("text")
    if not new_text or new_text.startswith("/"):
        return

    prefix = "<b>Mesaj din partea Administratiei:</b>"
    full_text = f"{prefix}\n{new_text}"

    key = (user_chat_id, user_msg_id)
    channel_msg_id = message_map.get(key)

    if not channel_msg_id:
        return

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    username = get_username(user_id)
    print(f"[{timestamp}] EDIT TEXT DE LA {user_id} ({username}) -> EDIT PE CANAL (msg_id={channel_msg_id})")

    requests.post(f"{API_URL}/editMessageText", data={
        "chat_id": CHANNEL_ID,
        "message_id": channel_msg_id,
        "text": full_text,
        "parse_mode": "HTML"
    })


def main():
    offset = 0

    while True:
        try:
            check_scheduled_reminders()

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

                # mesaje noi
                message = update.get("message")
                if message:
                    handle_new_message(message)

                # mesaje editate
                edited = update.get("edited_message")
                if edited:
                    handle_edited_message(edited)

        except Exception as e:
            print("Eroare:", e)
            time.sleep(3)


if __name__ == "__main__":
    main()