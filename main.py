import random
import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from flask import Flask
import threading

# ==== TELEGRAM BOT ====
TOKEN = os.environ.get("TOKEN", "запасной_токен")
REDDIT_URL = "https://www.reddit.com/r/memes/top.json?t=day&limit=25"
sent_memes = []


def get_fresh_memes():
    global sent_memes
    headers = {"User-Agent": "MemeBot/1.0"}
    response = requests.get(REDDIT_URL, headers=headers)
    data = response.json()

    all_memes = []
    for post in data["data"]["children"]:
        url = post["data"]["url"]
        if url.endswith((".jpg", ".jpeg", ".png", ".gif")):
            all_memes.append(url)

    fresh = [m for m in all_memes if m not in sent_memes]
    if not fresh:
        sent_memes = []
        fresh = all_memes
    return fresh


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я мем-бот!\n"
        "/meme — случайный мем\n"
        "/5 — пачка из 5 мемов\n"
        "/reset — сбросить историю"
    )


async def meme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global sent_memes
    fresh = get_fresh_memes()
    if fresh:
        url = random.choice(fresh)
        sent_memes.append(url)
        await update.message.reply_photo(photo=url, caption="Держи мем!")
    else:
        await update.message.reply_text("Не могу найти мемы. Попробуй позже.")


async def five(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global sent_memes
    fresh = get_fresh_memes()
    if fresh:
        chosen = random.sample(fresh, min(5, len(fresh)))
        sent_memes.extend(chosen)
        for url in chosen:
            await update.message.reply_photo(photo=url)
    else:
        await update.message.reply_text("Не могу найти мемы. Попробуй позже.")


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global sent_memes
    sent_memes = []
    await update.message.reply_text("История сброшена!")


# ==== KEEP ALIVE (веб-сервер) ====
app_flask = Flask(__name__)


@app_flask.route("/")
def home():
    return "Бот работает!"


def run_flask():
    app_flask.run(host="0.0.0.0", port=10000)


# ==== ЗАПУСК ====
if __name__ == "__main__":
    # Запускаем Flask в отдельном потоке
    threading.Thread(target=run_flask, daemon=True).start()

    # Запускаем Telegram бота
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("meme", meme))
    app.add_handler(CommandHandler("5", five))
    app.add_handler(CommandHandler("reset", reset))

    print("Бот запущен с Keep-Alive!")
    app.run_polling()