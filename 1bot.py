
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes

BOT_TOKEN = "8123533418:AAFS8i5oKp9WhmSS24KnxA_FbxFjdgvfcRE"
REQUIRED_CHANNEL = "@Restzona_tarjima_kinolar"

logging.basicConfig(level=logging.INFO)

async def check_subscription(user_id, app):
    try:
        member = await app.bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        return member.status in ["member","administrator","creator"]
    except:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await check_subscription(user_id, context.application):
        btn = [[InlineKeyboardButton("📥 Kanalga obuna bo‘lish", url=f"https://t.me/{REQUIRED_CHANNEL[1:]}")],
               [InlineKeyboardButton("✔ Obuna bo‘ldim", callback_data="check_sub")]]
        await update.message.reply_text("👉 Avval kanalga obuna bo‘ling", reply_markup=InlineKeyboardMarkup(btn))
        return
    await update.message.reply_text("🎬 Kino nomini yozing — qidirib beraman!")

async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if not await check_subscription(user_id, context.application):
        await query.edit_message_text("❌ Siz hali kanalga obuna bo‘lmagansiz!")
        return

    await query.edit_message_text("✔ Obuna tasdiqlandi! Endi kino nomini yuboring.")

async def search_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await check_subscription(user_id, context.application):
        btn = [[InlineKeyboardButton("📥 Kanal", url=f"https://t.me/{REQUIRED_CHANNEL[1:]}")],
               [InlineKeyboardButton("✔ Obuna bo‘ldim", callback_data="check_sub")]]
        await update.message.reply_text("👉 Avval kanalga obuna bo‘ling", reply_markup=InlineKeyboardMarkup(btn))
        return

    query = update.message.text.lower()
    await update.message.reply_text("🔍 Qidirilmoqda...")

    # Demo javob (kanaldan real qidiruv uchun Telegram API bilan forward/parse qilish kerak)
    await update.message.reply_text(
    f"""🎬 Topilgan kino:
🎞 Nom: {title}
📅 Yil: {year}
⭐ Reyting: {rating}
"""
)

**{query.title()}**

"⚠ Hozircha demo javob.")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(verify, pattern="check_sub"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_movie))

    app.run_polling()

if __name__ == "__main__":
    main()
