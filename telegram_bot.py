import json
import os
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# Bot tokeni
TOKEN = "7890308345:AAHXg6B_W5g5BVjh2zsqDXMBmf3qAwI4k0M"

# Admin ID (o'zingizning Telegram ID'ingizni qo'ying)
ADMIN_ID = 1621102297  # Bu yerga o'zingizning Telegram ID'ingizni kiriting

# Ma'lumotlarni saqlash uchun JSON fayl
DATA_FILE = "movies.json"

# Ma'lumotlarni yuklash funksiyasi
def load_movies():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

# Ma'lumotlarni saqlash funksiyasi
def save_movies(movies):
    with open(DATA_FILE, "w") as f:
        json.dump(movies, f, indent=4)

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom. Men kino botiman. Kino ID'sini yuboring, men sizga kino yuboraman. "
        "Agar admin bo'lsangiz, kino yuklash uchun video fayl yuboring."
    )

# Admin kino yuklashi
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("Faqat admin kino yuklay oladi!")
        return

    video = update.message.video
    if not video:
        await update.message.reply_text("Iltimos, video fayl yuboring!")
        return

    # Fayl ID'sini olish
    file_id = video.file_id
    movie_id = str(len(load_movies()) + 1)  # Oddiy ID generatsiyasi
    movies = load_movies()
    movies[movie_id] = file_id
    save_movies(movies)

    await update.message.reply_text(f"Kino muvaffaqiyatli yuklandi! ID: {movie_id}")

# Foydalanuvchi kino ID kiritganda
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    movie_id = update.message.text
    movies = load_movies()

    if movie_id in movies:
        file_id = movies[movie_id]
        await update.message.reply_video(file_id)
    else:
        await update.message.reply_text("Bunday ID bilan kino topilmadi!")

# Xato loglari
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Xato yuz berdi: {context.error}")

def main():
    # Botni ishga tushirish
    app = Application.builder().token(TOKEN).build()

    # Handlerlar
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_error_handler(error)

    # Botni polling rejimida ishga tushirish
    print("Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()