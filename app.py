import os
import requests
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)

# cheie pentru sesiune (schimbă cu ceva random și ține-l secret)
app.secret_key = os.environ.get("SECRET_KEY", "schimba_asta_cu_ceva_random_si_lung")

# login fix
USERNAME = "ciobanu"
PASSWORD = "bizaR.@1"

# token si chat id din variabile de mediu
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")


def is_logged_in():
    return session.get("logged_in") is True


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form.get("username")
        pwd = request.form.get("password")

        if user == USERNAME and pwd == PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("panel"))
        else:
            return render_template("login.html", error="Date de logare greșite")

    if is_logged_in():
        return redirect(url_for("panel"))
    return render_template("login.html")


@app.route("/panel", methods=["GET", "POST"])
def panel():
    if not is_logged_in():
        return redirect(url_for("login"))

    status = None
    message_content = ""

    if request.method == "POST":
        message_content = request.form.get("message", "").strip()

        if not TELEGRAM_TOKEN or not CHAT_ID:
            status = ("Lipsesc TELEGRAM_TOKEN sau CHAT_ID în variabilele de mediu", "error")
        elif not message_content:
            status = ("Mesaj gol", "warning")
        else:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            data = {
                "chat_id": CHAT_ID,
                "text": message_content,
                "parse_mode": "HTML"
            }
            try:
                r = requests.post(url, data=data, timeout=5)
                if r.status_code == 200:
                    status = ("Mesaj trimis cu succes", "success")
                    message_content = ""
                else:
                    status = (f"Eroare {r.status_code}", "error")
            except Exception as e:
                status = (f"Eroare: {str(e)[:80]}", "error")

    return render_template("panel.html", status=status, message_content=message_content)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    # pentru local
    app.run(host="0.0.0.0", port=5000, debug=True)
