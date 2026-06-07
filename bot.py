import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, CallbackQueryHandler, filters, ContextTypes

BOT_TOKEN = "8348876985:AAHeUsnnvlAyCyQX4jhxTMGucPzcxBxKss4"
CHANNEL_ID = "@Craaaazyhouse"
CHANNEL_LINK = "https://t.me/Craaaazyhouse"
ADMIN_ID = 1233167568

logging.basicConfig(level=logging.INFO)
user_sessions = {}
blocked_users = set()
waiting_for_message = set()

async def is_member(context, user_id):
    try:
        member = await context.bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

def main_menu():
    keyboard = [
        [InlineKeyboardButton("📨 ارسال پیام ناشناس", callback_data="send_msg")],
        [InlineKeyboardButton("📢 کانال ما", url=CHANNEL_LINK)],
        [InlineKeyboardButton("❓ راهنما", callback_data="help")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update, context):
    user = update.effective_user
    if user.id in blocked_users:
        await update.message.reply_text("❌ شما مسدود شده‌اید.")
        return
    member = await is_member(context, user.id)
    if not member:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("عضویت در کانال 📢", url=CHANNEL_LINK)],
            [InlineKeyboardButton("✅ عضو شدم", callback_data="check_join")]
        ])
        await update.message.reply_text("👋 سلام!\n\nبرای استفاده از ربات، اول باید عضو کانال ما بشی 👇", reply_markup=keyboard)
        return
    await update.message.reply_text(f"👋 سلام {user.first_name}!\n\n🎭 اینجا می‌تونی هر حرف، سوال، انتقاد یا پیشنهادی داری رو به صورت ناشناس بفرستی.\n\nاز منوی زیر انتخاب کن 👇", reply_markup=main_menu())

async def button_handler(update, context):
    query = update.callback_query
    user = query.from_user
    await query.answer()
    if query.data == "check_join":
        member = await is_member(context, user.id)
        if member:
            await query.edit_message_text("✅ عضویتت تایید شد!\n\nاز منوی زیر انتخاب کن 👇", reply_markup=main_menu())
        else:
            await query.answer("❌ هنوز عضو نشدی!", show_alert=True)
        return
    if query.data == "send_msg":
        if user.id in blocked_users:
            await query.answer("❌ شما مسدود شده‌اید!", show_alert=True)
            return
        waiting_for_message.add(user.id)
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])
        await query.edit_message_text("📨 پیامت رو بنویس و بفرست 👇", reply_markup=keyboard)
        return
    if query.data == "help":
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])
        await query.edit_message_text("❓ راهنما:\n\n1️⃣ روی ارسال پیام ناشناس کلیک کن\n2️⃣ پیامت رو بنویس\n3️⃣ پیامت به صورت ناشناس ارسال میشه\n\n⚠️ هویت شما کاملاً محفوظ میمونه", reply_markup=keyboard)
        return
    if query.data == "back":
        await query.edit_message_text("از منوی زیر انتخاب کن 👇", reply_markup=main_menu())
        return
    if query.data.startswith("post_"):
        uid = int(query.data.split("_")[1])
        data = user_sessions.get(uid)
        if data:
            await context.bot.send_message(chat_id=CHANNEL_ID, text=f"📨 پیام ناشناس:\n\n{data['text']}")
            await query.edit_message_reply_markup(reply_markup=None)
            await context.bot.send_message(chat_id=ADMIN_ID, text="✅ پیام به کانال پست شد!")
        return
    if query.data.startswith("block_"):
        uid = int(query.data.split("_")[1])
        blocked_users.add(uid)
        await query.edit_message_reply_markup(reply_markup=None)
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"🚫 کاربر {uid} مسدود شد!")
        return

async def handle_message(update, context):
    user = update.effective_user
    message = update.message
    if user.id in blocked_users:
        await message.reply_text("❌ شما مسدود شده‌اید.")
        return
    if user.id == ADMIN_ID:
        if message.reply_to_message:
            for uid, data in user_sessions.items():
                if data['msg_id'] == message.reply_to_message.message_id:
                    await context.bot.send_message(chat_id=uid, text=f"📩 جواب:\n\n{message.text}")
                    await message.reply_text("✅ جواب ارسال شد!")
                    return
        await message.reply_text("⚠️ روی پیام کاربر Reply کن!")
        return
    if user.id in waiting_for_message:
        waiting_for_message.discard(user.id)
        name = user.full_name or "ناشناس"
        username = f"@{user.username}" if user.username else "ندارد"
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("📢 پست در کانال", callback_data=f"post_{user.id}"), InlineKeyboardButton("🚫 بلاک", callback_data=f"block_{user.id}")]])
        sent = await context.bot.send_message(chat_id=ADMIN_ID, text=f"📨 پیام جدید:\n\n{message.text}\n\n👤 نام: {name}\n🔗 یوزر: {username}\n🆔 آیدی: {user.id}", reply_markup=keyboard)
        user_sessions[user.id] = {'msg_id': sent.message_id, 'text': message.text}
        await message.reply_text("✅ پیامت ارسال شد!\n\nاگه جواب داشت بهت میگم 😊", reply_markup=main_menu())
        return
    await message.reply_text("از منوی زیر انتخاب کن 👇", reply_markup=main_menu())

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
