import logging
import json
from datetime import datetime, date
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, CallbackQueryHandler, filters

BOT_TOKEN = "8348876985:AAHeUsnnvlAyCyQX4jhxTMGucPzcxBxKss4"
CHANNEL_ID = "@Craaaazyhouse"
CHANNEL_LINK = "https://t.me/Craaaazyhouse"
ADMIN_ID = 1233167568
MAX_MESSAGES_PER_DAY = 10

logging.basicConfig(level=logging.INFO)

user_sessions = {}
blocked_users = set()
silenced_users = set()
waiting_for_message = set()
waiting_for_broadcast = False
all_users = set()
user_message_count = {}
user_last_date = {}


async def is_member(context, user_id):
    try:
        member = await context.bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


def check_daily_limit(user_id):
    today = date.today().isoformat()
    if user_last_date.get(user_id) != today:
        user_message_count[user_id] = 0
        user_last_date[user_id] = today
    return user_message_count.get(user_id, 0) < MAX_MESSAGES_PER_DAY


def increment_message_count(user_id):
    user_message_count[user_id] = user_message_count.get(user_id, 0) + 1


def main_menu():
    keyboard = [
        [InlineKeyboardButton("📨 ارسال پیام ناشناس", callback_data="send_msg")],
        [InlineKeyboardButton("🖼️ ارسال عکس ناشناس", callback_data="send_photo")],
        [InlineKeyboardButton("📊 نظرسنجی ناشناس", callback_data="send_poll")],
        [InlineKeyboardButton("📢 کانال ما", url=CHANNEL_LINK)],
        [InlineKeyboardButton("❓ راهنما", callback_data="help")]
    ]
    return InlineKeyboardMarkup(keyboard)


def admin_menu():
    keyboard = [
        [InlineKeyboardButton("📊 آمار", callback_data="admin_stats")],
        [InlineKeyboardButton("🚫 لیست بلاک شده‌ها", callback_data="admin_blocklist")],
        [InlineKeyboardButton("📢 پیام همگانی", callback_data="admin_broadcast")],
    ]
    return InlineKeyboardMarkup(keyboard)


async def start(update, context):
    user = update.effective_user
    all_users.add(user.id)

    if user.id == ADMIN_ID:
        await update.message.reply_text(
            "👋 سلام ادمین!\n\nپنل مدیریت:",
            reply_markup=admin_menu()
        )
        return

    if user.id in blocked_users:
        await update.message.reply_text("❌ شما مسدود شده‌اید.")
        return

    member = await is_member(context, user.id)
    if not member:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("عضویت در کانال 📢", url=CHANNEL_LINK)],
            [InlineKeyboardButton("✅ عضو شدم", callback_data="check_join")]
        ])
        await update.message.reply_text(
            "👋 سلام!\n\nبرای استفاده از ربات، اول باید عضو کانال ما بشی 👇",
            reply_markup=keyboard
        )
        return

    await update.message.reply_text(
        f"🌪️ درود بر {user.first_name} 🌪️\n\n"
        "اینجا می‌تونی هر حرف، سؤال، انتقاد، پیشنهاد یا درد دلی که داری رو به صورت ناشناس بفرستی.\n"
        "هویتت نمایش داده نمیشه ⚡\n\n"
        "از منوی زیر انتخاب کن 👇",
        reply_markup=main_menu()
    )


async def button_handler(update, context):
    global waiting_for_broadcast
    query = update.callback_query
    user = query.from_user
    await query.answer()

    if query.data == "check_join":
        member = await is_member(context, user.id)
        if member:
            await query.edit_message_text(
                f"🌪️ درود بر {user.first_name} 🌪️\n\n"
                "اینجا می‌تونی هر حرف، سؤال، انتقاد، پیشنهاد یا درد دلی که داری رو به صورت ناشناس بفرستی.\n"
                "هویتت نمایش داده نمیشه ⚡\n\n"
                "از منوی زیر انتخاب کن 👇",
                reply_markup=main_menu()
            )
        else:
            await query.answer("❌ هنوز عضو نشدی!", show_alert=True)
        return

    if query.data == "send_msg":
        if user.id in blocked_users:
            await query.answer("❌ شما مسدود شده‌اید!", show_alert=True)
            return
        if not check_daily_limit(user.id):
            await query.answer(f"❌ سقف روزانه {MAX_MESSAGES_PER_DAY} پیام!", show_alert=True)
            return
        waiting_for_message.add((user.id, "text"))
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])
        await query.edit_message_text("📨 پیامت رو بنویس و بفرست 👇", reply_markup=keyboard)
        return

    if query.data == "send_photo":
        if user.id in blocked_users:
            await query.answer("❌ شما مسدود شده‌اید!", show_alert=True)
            return
        if not check_daily_limit(user.id):
            await query.answer(f"❌ سقف روزانه {MAX_MESSAGES_PER_DAY} پیام!", show_alert=True)
            return
        waiting_for_message.add((user.id, "photo"))
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])
        await query.edit_message_text("🖼️ عکست رو بفرست 👇", reply_markup=keyboard)
        return

    if query.data == "send_poll":
        if user.id in blocked_users:
            await query.answer("❌ شما مسدود شده‌اید!", show_alert=True)
            return
        waiting_for_message.add((user.id, "poll"))
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])
        await query.edit_message_text(
            "📊 نظرسنجی رو بفرست 👇\n\nاول سوال رو بنویس، بعد گزینه‌ها رو با خط جدید بنویس:\n\nمثال:\nسوال من\nگزینه ۱\nگزینه ۲\nگزینه ۳",
            reply_markup=keyboard
        )
        return

    if query.data == "help":
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])
        await query.edit_message_text(
            "❓ راهنما:\n\n"
            "1️⃣ روی ارسال پیام ناشناس کلیک کن\n"
            "2️⃣ پیامت رو بنویس\n"
            "3️⃣ پیامت به صورت ناشناس ارسال میشه\n\n"
            f"⚠️ سقف روزانه: {MAX_MESSAGES_PER_DAY} پیام\n"
            "🔒 هویت شما کاملاً محفوظ میمونه",
            reply_markup=keyboard
        )
        return

    if query.data == "back":
        await query.edit_message_text(
            "از منوی زیر انتخاب کن 👇",
            reply_markup=main_menu()
        )
        return

    if query.data == "admin_stats":
        blocked_count = len(blocked_users)
        silenced_count = len(silenced_users)
        total_users = len(all_users)
        await query.edit_message_text(
            f"📊 آمار ربات:\n\n"
            f"👥 کل کاربران: {total_users}\n"
            f"🚫 بلاک شده‌ها: {blocked_count}\n"
            f"🔇 سایلنت شده‌ها: {silenced_count}\n",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_back")]])
        )
        return

    if query.data == "admin_blocklist":
        if blocked_users:
            text = "🚫 لیست بلاک شده‌ها:\n\n"
            for uid in blocked_users:
                text += f"🆔 {uid}\n"
        else:
            text = "✅ هیچ کاربری بلاک نشده!"
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_back")]])
        )
        return

    if query.data == "admin_broadcast":
        waiting_for_broadcast = True
        await query.edit_message_text(
            "📢 پیام همگانی رو بنویس:\n\nاین پیام برای همه کاربران فرستاده میشه!",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 لغو", callback_data="admin_back")]])
        )
        return

    if query.data == "admin_back":
        waiting_for_broadcast = False
        await query.edit_message_text(
            "👋 سلام ادمین!\n\nپنل مدیریت:",
            reply_markup=admin_menu()
        )
        return

    if query.data.startswith("post_"):
        uid = int(query.data.split("_")[1])
        data = user_sessions.get(uid)
        if data:
            await context.bot.send_message(
                chat_id=CHANNEL_ID,
                text=f"📨 پیام ناشناس:\n\n{data['text']}"
            )
            await query.edit_message_reply_markup(reply_markup=None)
            await context.bot.send_message(chat_id=ADMIN_ID, text="✅ پیام به کانال پست شد!")
        return

    if query.data.startswith("block_"):
        uid = int(query.data.split("_")[1])
        blocked_users.add(uid)
        await query.edit_message_reply_markup(reply_markup=None)
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"🚫 کاربر {uid} مسدود شد!")
        return

    if query.data.startswith("unblock_"):
        uid = int(query.data.split("_")[1])
        blocked_users.discard(uid)
        await query.edit_message_reply_markup(reply_markup=None)
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"✅ کاربر {uid} آنبلاک شد!")
        return

    if query.data.startswith("silence_"):
        uid = int(query.data.split("_")[1])
        silenced_users.add(uid)
        await query.edit_message_reply_markup(reply_markup=None)
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"🔇 کاربر {uid} سایلنت شد!")
        return


async def handle_message(update, context):
    global waiting_for_broadcast
    user = update.effective_user
    message = update.message

    all_users.add(user.id)

    if user.id in blocked_users:
        await message.reply_text("❌ شما مسدود شده‌اید.")
        return

    if user.id == ADMIN_ID:
        if waiting_for_broadcast:
            waiting_for_broadcast = False
            sent_count = 0
            for uid in all_users:
                if uid != ADMIN_ID:
                    try:
                        await context.bot.send_message(
                            chat_id=uid,
                            text=f"📢 پیام از کانال:\n\n{message.text}"
                        )
                        sent_count += 1
                    except:
                        pass
            await message.reply_text(f"✅ پیام به {sent_count} نفر ارسال شد!", reply_markup=admin_menu())
            return

        if message.reply_to_message:
            for uid, data in user_sessions.items():
                if data['msg_id'] == message.reply_to_message.message_id:
                    if uid not in silenced_users:
                        await context.bot.send_message(
                            chat_id=uid,
                            text=f"📩 جواب:\n\n{message.text}"
                        )
                    await message.reply_text("✅ جواب ارسال شد!")
                    return
        await message.reply_text("⚠️ روی پیام کاربر Reply کن!", reply_markup=admin_menu())
        return

    waiting_entry = None
    for entry in waiting_for_message:
        if entry[0] == user.id:
            waiting_entry = entry
            break

    if waiting_entry:
        waiting_for_message.discard(waiting_entry)
        msg_type = waiting_entry[1]

        if not check_daily_limit(user.id):
            await message.reply_text(f"❌ سقف روزانه {MAX_MESSAGES_PER_DAY} پیام رو رد کردی!")
            return

        increment_message_count(user.id)
        name = user.full_name or "ناشناس"
        username = f"@{user.username}" if user.username else "ندارد"

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📢 پست در کانال", callback_data=f"post_{user.id}"),
                InlineKeyboardButton("🚫 بلاک", callback_data=f"block_{user.id}")
            ],
            [
                InlineKeyboardButton("🔇 سایلنت", callback_data=f"silence_{user.id}"),
                InlineKeyboardButton("✅ آنبلاک", callback_data=f"unblock_{user.id}")
            ]
        ])

        if msg_type == "text" and message.text:
            sent = await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"📨 پیام جدید:\n\n{message.text}\n\n👤 نام: {name}\n🔗 یوزر: {username}\n🆔 آیدی: {user.id}",
                reply_markup=keyboard
            )
            user_sessions[user.id] = {'msg_id': sent.message_id, 'text': message.text}

        elif msg_type == "photo" and message.photo:
            sent = await context.bot.send_photo(
                chat_id=ADMIN_ID,
                photo=message.photo[-1].file_id,
                caption=f"🖼️ عکس ناشناس:\n\n👤 نام: {name}\n🔗 یوزر: {username}\n🆔 آیدی: {user.id}",
                reply_markup=keyboard
            )
            user_sessions[user.id] = {'msg_id': sent.message_id, 'text': '🖼️ عکس'}

        elif msg_type == "poll" and message.text:
            lines = message.text.strip().split('\n')
            if len(lines) >= 3:
                question = lines[0]
                options = lines[1:]
                await context.bot.send_poll(
                    chat_id=ADMIN_ID,
                    question=f"📊 نظرسنجی ناشناس:\n{question}",
                    options=options
                )
                await context.bot.send_message(
                    chat_id=ADMIN_ID,
                    text=f"👤 نام: {name}\n🔗 یوزر: {username}\n🆔 آیدی: {user.id}",
                    reply_markup=keyboard
                )
                user_sessions[user.id] = {'msg_id': 0, 'text': '📊 نظرسنجی'}
            else:
                await message.reply_text("❌ فرمت اشتباه! سوال و حداقل ۲ گزینه بنویس!")
                return

        await message.reply_text(
            "✅ پیامت ارسال شد!\n\nاگه جواب داشت بهت میگم 😊",
            reply_markup=main_menu()
        )
        return

    await message.reply_text("از منوی زیر انتخاب کن 👇", reply_markup=main_menu())


async def handle_photo(update, context):
    user = update.effective_user
    all_users.add(user.id)

    if user.id in blocked_users:
        return

    waiting_entry = None
    for entry in waiting_for_message:
        if entry[0] == user.id and entry[1] == "photo":
            waiting_entry = entry
            break

    if waiting_entry:
        waiting_for_message.discard(waiting_entry)
        name = user.full_name or "ناشناس"
        username = f"@{user.username}" if user.username else "ندارد"

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📢 پست در کانال", callback_data=f"post_{user.id}"),
                InlineKeyboardButton("🚫 بلاک", callback_data=f"block_{user.id}")
            ],
            [
                InlineKeyboardButton("🔇 سایلنت", callback_data=f"silence_{user.id}"),
                InlineKeyboardButton("✅ آنبلاک", callback_data=f"unblock_{user.id}")
            ]
        ])

        sent = await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=update.message.photo[-1].file_id,
            caption=f"🖼️ عکس ناشناس:\n\n👤 نام: {name}\n🔗 یوزر: {username}\n🆔 آیدی: {user.id}",
            reply_markup=keyboard
        )
        user_sessions[user.id] = {'msg_id': sent.message_id, 'text': '🖼️ عکس'}
        await update.message.reply_text(
            "✅ عکست ارسال شد!\n\nاگه جواب داشت بهت میگم 😊",
            reply_markup=main_menu()
        )


async def unblock_command(update, context):
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        uid = int(context.args[0])
        blocked_users.discard(uid)
        await update.message.reply_text(f"✅ کاربر {uid} آنبلاک شد!")
    except:
        await update.message.reply_text("❌ آیدی کاربر رو بنویس!\nمثال: /unblock 123456789")


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("unblock", unblock_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()


if __name__ == "__main__":
    main()
