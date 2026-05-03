import random
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = "8404106428:AAE3hHtFiBl_EYMrxt9cPdyVJsawx_LU-Vk"
REDDIT_URL = "https://www.reddit.com/r/memes/top.json?t=day&limit=25"

# Список уже отправленных URL (чтобы не повторяться)
sent_memes = []


def get_fresh_memes():
    """
    Забирает с Reddit мемы, которые ещё не отправляли.
    Если все 25 уже были — сбрасывает историю и начинает заново.
    """
    global sent_memes

    headers = {"User-Agent": "MemeBot/1.0"}
    response = requests.get(REDDIT_URL, headers=headers)
    data = response.json()

    all_memes = []
    for post in data["data"]["children"]:
        url = post["data"]["url"]
        if url.endswith((".jpg", ".jpeg", ".png", ".gif")):
            all_memes.append(url)

    # Отсеиваем уже отправленные
    fresh = [m for m in all_memes if m not in sent_memes]

    # Если свежих не осталось — сбрасываем историю
    if not fresh:
        sent_memes = []
        fresh = all_memes

    return fresh


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я мем-бот!\n"
        "/meme — случайный мем\n"
        "/5 — пачка из 5 мемов\n"
        "/reset — сбросить историю мемов"
    )


async def meme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global sent_memes

    fresh = get_fresh_memes()
    if fresh:
        url = random.choice(fresh)
        sent_memes.append(url)  # запоминаем что отправили
        await update.message.reply_photo(photo=url, caption="Держи мем!")
    else:
        await update.message.reply_text("Не могу найти мемы. Попробуй позже.")


async def five(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global sent_memes

    fresh = get_fresh_memes()
    if fresh:
        # Берём до 5 штук
        chosen = random.sample(fresh, min(5, len(fresh)))
        sent_memes.extend(chosen)  # добавляем все выбранные в историю
        for url in chosen:
            await update.message.reply_photo(photo=url)
    else:
        await update.message.reply_text("Не могу найти мемы. Попробуй позже.")


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сбрасывает историю отправленных мемов"""
    global sent_memes
    sent_memes = []
    await update.message.reply_text("История сброшена! Мемы могут повторяться.")


app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("meme", meme))
app.add_handler(CommandHandler("5", five))
app.add_handler(CommandHandler("reset", reset))

print("Бот запущен с защитой от повторов!")
app.run_polling()