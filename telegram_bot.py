import json
import os
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

# Bot tokeni
TOKEN = "7890308345:AAHXg6B_W5g5BVjh2zsqDXMBmf3qAwI4k0M"

# Ma'lumotlarni saqlash uchun JSON fayllar
DATA_FILE = "movies.json"
ADMINS_FILE = "admins.json"

# Conversation states
DESCRIPTION = 1

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

# Adminlarni yuklash funksiyasi
def load_admins():
    if os.path.exists(ADMINS_FILE):
        with open(ADMINS_FILE, "r") as f:
            return json.load(f)
    return []

# Adminlarni saqlash funksiyasi
def save_admins(admins):
    with open(ADMINS_FILE, "w") as f:
        json.dump(admins, f, indent=4)

# Admin tekshiruvi
def is_admin(user_id):
    admins = load_admins()
    return str(user_id) in admins

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom! Men kino botiman. Kino ID'sini yuboring, men sizga kino yuboraman. "
        "Agar admin bo'lsangiz, quyidagi komandalarni ishlating:\n"
        "/addadmin <user_id> - Yangi admin qo'shish\n"
        "/removeadmin <user_id> - Adminni o'chirish\n"
        "/delete <movie_id> - Kino o'chirish"
    )

# Yangi admin qo'shish
async def add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if not is_admin(user_id):
        await update.message.reply_text("Faqat adminlar yangi admin qo'sha oladi!")
        return

    if len(context.args) != 1:
        await update.message.reply_text("Iltimos, foydalanuvchi ID'sini kiriting: /addadmin <user_id>")
        return

    new_admin_id = context.args[0]
    admins = load_admins()
    if new_admin_id not in admins:
        admins.append(new_admin_id)
        save_admins(admins)
        await update.message.reply_text(f"Admin {new_admin_id} muvaffaqiyatli qo'shildi!")
    else:
        await update.message.reply_text(f"{new_admin_id} allaqachon admin!")

# Adminni o'chirish
async def remove_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if not is_admin(user_id):
        await update.message.reply_text("Faqat adminlar adminni o'chira oladi!")
        return

    if len(context.args) != 1:
        await update.message.reply_text("Iltimos, foydalanuvchi ID'sini kiriting: /removeadmin <user_id>")
        return

    admin_id = context.args[0]
    admins = load_admins()
    if admin_id in admins:
        admins.remove(admin_id)
        save_admins(admins)
        await update.message.reply_text(f"Admin {admin_id} muvaffaqiyatli o'chirildi!")
    else:
        await update.message.reply_text(f"{admin_id} adminlar ro'yxatida yo'q!")

# Video yuklashda tavsif so'rash
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if not is_admin(user_id):
        await update.message.reply_text("Faqat admin kino yuklay oladi!")
        return

    video = update.message.video
    if not video:
        await update.message.reply_text("Iltimos, video fayl yuboring!")
        return

    # Video fayl ID'sini saqlash
    context.user_data['video_file_id'] = video.file_id
    await update.message.reply_text("Iltimos, video uchun tavsif (description) yuboring.")
    return DESCRIPTION

# Tavsifni saqlash
async def save_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    description = update.message.text
    video_file_id = context.user_data.get('video_file_id')
    if not video_file_id:
        await update.message.reply_text("Xato: Video fayli topilmadi. Qaytadan video yuboring.")
        return ConversationHandler.END

    movies = load_movies()
    movie_id = str(len(movies) + 1)  # Oddiy ID generatsiyasi
    movies[movie_id] = {
        'file_id': video_file_id,
        'description': description
    }
    save_movies(movies)

    await update.message.reply_text(f"Kino muvaffaqiyatli yuklandi! ID: {movie_id}\nTavsif: {description}")
    context.user_data.clear()
    return ConversationHandler.END

# Tavsif kiritishni bekor qilish
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Video yuklash bekor qilindi.")
    context.user_data.clear()
    return ConversationHandler.END

# Kino o'chirish (faqat adminlar uchun)
async def delete_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if not is_admin(user_id):
        await update.message.reply_text("Faqat adminlar kino o'chira oladi!")
        return

    if len(context.args) != 1:
        await update.message.reply_text("Iltimos, kino ID'sini kiriting: /delete <movie_id>")
        return

    movie_id = context.args[0]
    movies = load_movies()
    if movie_id in movies:
        del movies[movie_id]
        save_movies(movies)
        await update.message.reply_text(f"Kino (ID: {movie_id}) muvaffaqiyatli o'chirildi!")
    else:
        await update.message.reply_text("Bunday ID bilan kino topilmadi!")

# Foydalanuvchi kino ID kiritganda
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    movie_id = update.message.text
    movies = load_movies()

    if movie_id in movies:
        file_id = movies[movie_id]['file_id']
        description = movies[movie_id].get('description', 'Tavsif yo‘q')
        await update.message.reply_video(file_id, caption=f"ID: {movie_id}\nTavsif: {description}")
    else:
        await update.message.reply_text("Bunday ID bilan kino topilmadi!")

# Xato loglari
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Xato yuz berdi: {context.error}")

def main():
    # Botni ishga tushirish
    app = Application.builder().token(TOKEN).build()

    # Conversation handler for video upload with description
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.VIDEO, handle_video)],
        states={
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_description)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Handlerlar
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addadmin", add_admin))
    app.add_handler(CommandHandler("removeadmin", remove_admin))
    app.add_handler(CommandHandler("delete", delete_movie))
    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_error_handler(error)

    # Botni polling rejimida ishga tushirish
    print("Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()