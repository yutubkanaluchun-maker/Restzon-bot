import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
MOVIE_CHANNEL = os.getenv("MOVIE_CHANNEL")
REQUIRED_CHANNEL = os.getenv("REQUIRED_CHANNEL")

logging.basicConfig(level=logging.INFO)

MOVIE_FILE = "movies.txt"

async def check_subscription(user_id, app):
    try:
        member = await app.bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await check_subscription(user_id, context.application):
        btn = [
            [InlineKeyboardButton("📥 Kanalga obuna bo‘lish", url=f"https://t.me/Restzona_tarjima_kinolar")],
            [InlineKeyboardButton("✔ Obuna bo‘ldim", callback_data="check_sub")]
        ]
        await update.message.reply_text("👉 Avval kanalga obuna bo‘ling", reply_markup=InlineKeyboardMarkup(btn))
        return
    await update.message.reply_text("🎬 Kino nomini yozing yoki kategoriya bo‘yicha qidirish:
/category ACTION")

async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if not await check_subscription(user_id, context.application):
        await query.edit_message_text("❌ Siz hali kanalga obuna bo‘lmagansiz!")
        return
    await query.edit_message_text("✔ Obuna tasdiqlandi!
🎬 Endi kino nomini yuboring.")

async def admin_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    msg = update.message
    caption = msg.caption or "NO TITLE"
    import re
    match = re.search(r"@category\s+([A-Za-z0-9]+)", caption)
    category = match.group(1) if match else "UNCATEGORIZED"
    video = msg.video.file_id
    sent = await context.bot.send_video(chat_id=MOVIE_CHANNEL, video=video, caption=caption)
    movie_id = sent.message_id
    with open(MOVIE_FILE, "a", encoding="utf-8") as f:
        f.write(f"{caption}|{movie_id}|{category}\n")
    await msg.reply_text(f"✔ Kino yuklandi!\n🆔 ID: {movie_id}\n📂 Kategoriya: {category}")

async def search_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await check_subscription(user_id, context.application):
        return
    text = update.message.text
    category = text.replace("/category", "").strip().upper()
    if len(category) < 2:
        await update.message.reply_text("❗ Kategoriya nomini yozing.
/category ACTION")
        return
    if not os.path.exists(MOVIE_FILE):
        await update.message.reply_text("❌ Kino bazasi bo‘sh.")
        return
    found = False
    with open(MOVIE_FILE, "r", encoding="utf-8") as f:
        for row in f:
            title, msg_id, cat = row.strip().split("|")
            if cat.upper() == category:
                await update.message.bot.forward_message(
                    chat_id=update.effective_chat.id,
                    from_chat_id=MOVIE_CHANNEL,
                    message_id=int(msg_id)
                )
                found = True
    if not found:
        await update.message.reply_text("❌ Bu kategoriyada kino topilmadi.")

async def search_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await check_subscription(user_id, context.application):
        return
    q = update.message.text.lower()
    if not os.path.exists(MOVIE_FILE):
        await update.message.reply_text("❌ Kino yo‘q.")
        return
    with open(MOVIE_FILE, "r", encoding="utf-8") as f:
        for row in f:
            title, msg_id, cat = row.strip().split("|")
            if q in title.lower():
                await context.bot.forward_message(
                    chat_id=update.effective_chat.id,
                    from_chat_id=MOVIE_CHANNEL,
                    message_id=int(msg_id)
                )
                return
    await update.message.reply_text("❌ Bu nomdagi kino topilmadi.")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("category", search_category))
    app.add_handler(CallbackQueryHandler(verify, pattern="check_sub"))
    app.add_handler(MessageHandler(filters.VIDEO, admin_upload))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_movie))
    app.run_polling()

if __name__ == "__main__":
    main()
