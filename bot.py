import logging
from datetime import datetime, date
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMemberUpdated
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, CallbackQueryHandler, filters, ChatMemberHandler

BOT_TOKEN = "8348876985:AAHeUsnnvlAyCyQX4jhxTMGucPzcxBxKss4"
CHANNEL_ID = "@Craaaazyhouse"
CHANNEL_LINK = "https://t.me/Craaaazyhouse"
ADMIN_ID = 1233167568

logging.basicConfig(level=logging.INFO)

user_sessions = {}
blocked_users = set()
silenced_users = set()
vip_users = set()
waiting_for_message = set()
waiting_for_broadcast = False
waiting_for_scheduled = False
scheduled_time = None
all_users = set()
music_requests = []


async def is_member(context, user_id):
    try:
        member = await context.bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


def main_menu(user_id=None):
    keyboard = [
        [InlineKeyboardButton("📨 ارسال پیام ناشناس", callback_data="send_msg")],
        [InlineKeyboardButton("🖼️ ارسال عکس ناشناس", callback_data="send_photo")],
        [InlineKeyboardButton("🎵 درخواست موزیک", callback_data="send_music")],
        [InlineKeyboardButton("📊 نظرسنجی ناشناس", callback_data="send_poll")],
        [InlineKeyboardButton("📢 کانال ما", url=CHANNEL_LINK)],
        [InlineKeyboardButton("❓ راهنما", callback_data="help")]
    ]
    if user_id and user_id in vip_users:
        keyboard.insert(0, [InlineKeyboardButton("⭐ VIP", callback_data="vip_menu")])
    return InlineKeyboardMarkup(keyboard)


def admin_menu():
    keyboard = [
        [InlineKeyboardButton("📊 آمار کامل", callback_data="admin_stats")],
        [InlineKeyboardButton("🚫 لیست بلاک", callback_data="admin_blocklist"),
         InlineKeyboardButton("⭐ لیست VIP", callback_data="admin_viplist")],
        [InlineKeyboardButton("📢 پیام همگانی", callback_data="admin_broadcast")],
        [InlineKeyboardButton("⏰ پست زمان‌بندی شده", callback_data="admin_scheduled")],
        [InlineKeyboardButton("🎵 درخواست‌های موزیک", callback_data="admin_music")],
    ]
    return InlineKeyboardMarkup(keyboard)


async def start(update, context):
    user = update.effective_user
    all_users.add(user.id)

    if user.id == ADMIN_ID:
        await update.message.reply_text(
            "👋 سلام ادمین!\n\nپنل مدیریت کانال:",
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

    vip_badge = "⭐ " if user.id in vip_users else ""
    await update.message.reply_text(
        f"🌪️ درود بر {vip_badge}{user.first_name} 🌪️\n\n"
        "اینجا می‌تونی هر حرف، سؤال، انتقاد، پیشنهاد یا درد دلی که داری رو به صورت ناشناس بفرستی.\n"
        "هویتت نمایش داده نمیشه ⚡\n\n"
        "از منوی زیر انتخاب کن 👇",
        reply_markup=main_menu(user.id)
    )


async def track_channel_members(update, context):
    result = update.chat_member
    if not result:
        return

    old_status = result.old_chat_member.status
    new_status = result.new_chat_member.status
    user = result.new_chat_member.user

    if old_status in ["left", "kicked"] and new_status == "member":
        all_users.add(user.id)
        name = user.full_name or "ناشناس"
        username = f"@{user.username}" if user.username else "ندارد"
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🟢 عضو جدید!\n\n👤 نام: {name}\n🔗 یوزر: {username}\n🆔 آیدی: {user.id}\n\n📊 کل اعضا: {len(all_users)}"
        )

    elif old_status == "member" and new_status in ["left", "kicked"]:
        name = user.full_name or "ناشناس"
        username = f"@{user.username}" if user.username else "ندارد"
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🔴 عضو لفت داد!\n\n👤 نام: {name}\n🔗 یوزر: {username}\n🆔 آیدی: {user.id}"
        )


async def button_handler(update, context):
    global waiting_for_broadcast, waiting_for_scheduled
    query = update.callback_query
    user = query.from_user
    await query.answer()

    if query.data == "check_join":
        member = await is_member(context, user.id)
        if member:
            vip_badge = "⭐ " if user.id in vip_users else ""
            await query.edit_message_text(
                f"🌪️ درود بر {vip_badge}{user.first_name} 🌪️\n\n"
                "اینجا می‌تونی هر حرف، سؤال، انتقاد، پیشنهاد یا درد دلی که داری رو به صورت ناشناس بفرستی.\n"
                "هویتت نمایش داده نمیشه ⚡\n\n"
                "از منوی زیر انتخاب کن 👇",
                reply_markup=main_menu(user.id)
            )
        else:
            await query.answer("❌ هنوز عضو نشدی!", show_alert=True)
        return

    if query.data == "send_msg":
        if user.id in blocked_users:
            await query.answer("❌ شما مسدود شده‌اید!", show_alert=True)
            return
        waiting_for_message.add((user.id, "text"))
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])
        await query.edit_message_text("📨 پیامت رو بنویس و بفرست 👇", reply_markup=keyboard)
        return

    if query.data == "send_photo":
        if user.id in blocked_users:
            await query.answer("❌ شما مسدود شده‌اید!", show_alert=True)
            return
        waiting_for_message.add((user.id, "photo"))
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])
        await query.edit_message_text("🖼️ عکست رو بفرست 👇", reply_markup=keyboard)
        return

    if query.data == "send_music":
        if user.id in blocked_users:
            await query.answer("❌ شما مسدود شده‌اید!", show_alert=True)
            return
        waiting_for_message.add((user.id, "music"))
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])
        await query.edit_message_text(
            "🎵 درخواست موزیک:\n\nاسم آهنگ و خواننده رو بنویس 👇\nمثال: شادمهر عقیلی - دوست دارم",
            reply_markup=keyboard
        )
        return

    if query.data == "send_poll":
        if user.id in blocked_users:
            await query.answer("❌ شما مسدود شده‌اید!", show_alert=True)
            return
        waiting_for_message.add((user.id, "poll"))
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])
        await query.edit_message_text(
            "📊 نظرسنجی:\n\nسوال رو بنویس، بعد گزینه‌ها رو با خط جدید:\n\nمثال:\nبهترین سبک موزیک؟\nپاپ\nراک\nرپ\nکلاسیک",
            reply_markup=keyboard
        )
        return

    if query.data == "help":
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])
        await query.edit_message_text(
            "❓ راهنما:\n\n"
            "📨 پیام ناشناس - هر چیزی بفرست\n"
            "🖼️ عکس ناشناس - عکس بفرست\n"
            "🎵 درخواست موزیک - آهنگ درخواست بده\n"
            "📊 نظرسنجی - نظرسنجی بساز\n\n"
            "🔒 هویت شما کاملاً محفوظه",
            reply_markup=keyboard
        )
        return

    if query.data == "back":
        await query.edit_message_text(
            "از منوی زیر انتخاب کن 👇",
            reply_markup=main_menu(user.id)
        )
        return

    if query.data == "admin_stats":
        total = len(all_users)
        blocked = len(blocked_users)
        silenced = len(silenced_users)
        vip = len(vip_users)
        music = len(music_requests)
        await query.edit_message_text(
            f"📊 آمار کامل:\n\n"
            f"👥 کل کاربران: {total}\n"
            f"⭐ VIP: {vip}\n"
            f"🚫 بلاک: {blocked}\n"
            f"🔇 سایلنت: {silenced}\n"
            f"🎵 درخواست موزیک: {music}\n"
            f"📅 تاریخ: {datetime.now().strftime('%Y/%m/%d %H:%M')}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_back")]])
        )
        return

    if query.data == "admin_blocklist":
        if blocked_users:
            text = "🚫 لیست بلاک:\n\n" + "\n".join([f"🆔 {uid}" for uid in blocked_users])
        else:
            text = "✅ هیچ کاربری بلاک نشده!"
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_back")]])
        )
        return

    if query.data == "admin_viplist":
        if vip_users:
            text = "⭐ لیست VIP:\n\n" + "\n".join([f"🆔 {uid}" for uid in vip_users])
        else:
            text = "هیچ کاربر VIP نداری!"
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_back")]])
        )
        return

    if query.data == "admin_broadcast":
        waiting_for_broadcast = True
        waiting_for_scheduled = False
        await query.edit_message_text(
            "📢 پیام همگانی رو بنویس:\n\nبرای همه کاربران فرستاده میشه!",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 لغو", callback_data="admin_back")]])
        )
        return

    if query.data == "admin_scheduled":
        waiting_for_scheduled = True
        waiting_for_broadcast = False
        await query.edit_message_text(
            "⏰ پست زمان‌بندی شده:\n\nاول ساعت رو بنویس (مثال: 20:30)\nبعد در پیام بعدی متن پست رو بفرست:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 لغو", callback_data="admin_back")]])
        )
        return

    if query.data == "admin_music":
        if music_requests:
            text = "🎵 درخواست‌های موزیک:\n\n"
            for i, req in enumerate(music_requests[-10:], 1):
                text += f"{i}. {req['music']} - از {req['name']}\n"
        else:
            text = "🎵 هیچ درخواست موزیکی نیست!"
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_back")]])
        )
        return

    if query.data == "admin_back":
        waiting_for_broadcast = False
        waiting_for_scheduled = False
        await query.edit_message_text(
            "👋 سلام ادمین!\n\nپنل مدیریت کانال:",
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
            await query.answer("✅ پست شد!", show_alert=True)
        return

    if query.data.startswith("reply_"):
        uid = int(query.data.split("_")[1])
        waiting_for_message.add((ADMIN_ID, f"reply_{uid}"))
        await query.answer("✏️ جوابت رو بنویس!", show_alert=True)
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"✏️ جواب برای کاربر {uid} رو بنویس:"
        )
        return

    if query.data.startswith("block_"):
        uid = int(query.data.split("_")[1])
        blocked_users.add(uid)
        silenced_users.discard(uid)
        await query.answer(f"🚫 بلاک شد!", show_alert=True)
        await query.edit_message_reply_markup(reply_markup=None)
        return

    if query.data.startswith("unblock_"):
        uid = int(query.data.split("_")[1])
        blocked_users.discard(uid)
        await query.answer(f"✅ آنبلاک شد!", show_alert=True)
        await query.edit_message_reply_markup(reply_markup=None)
        return

    if query.data.startswith("silence_"):
        uid = int(query.data.split("_")[1])
        silenced_users.add(uid)
        await query.answer(f"🔇 سایلنت شد!", show_alert=True)
        await query.edit_message_reply_markup(reply_markup=None)
        return

    if query.data.startswith("vip_"):
        uid = int(query.data.split("_")[1])
        vip_users.add(uid)
        await query.answer(f"⭐ VIP شد!", show_alert=True)
        await query.edit_message_reply_markup(reply_markup=None)
        return


async def handle_message(update, context):
    global waiting_for_broadcast, waiting_for_scheduled, scheduled_time
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
                        await context.bot.send_message(chat_id=uid, text=f"📢 پیام از کانال:\n\n{message.text}")
                        sent_count += 1
                    except:
                        pass
            await message.reply_text(f"✅ پیام به {sent_count} نفر ارسال شد!", reply_markup=admin_menu())
            return

        if waiting_for_scheduled:
            if scheduled_time is None:
                try:
                    scheduled_time = message.text.strip()
                    await message.reply_text(f"⏰ ساعت {scheduled_time} ثبت شد!\n\nحالا متن پست رو بفرست:")
                except:
                    await message.reply_text("❌ فرمت اشتباه! مثال: 20:30")
            else:
                waiting_for_scheduled = False
                await message.reply_text(
                    f"✅ پست برای ساعت {scheduled_time} ذخیره شد!\n\n⚠️ توجه: ارسال خودکار نیاز به سرور دائمی داره. الان باید دستی پست کنی.",
                    reply_markup=admin_menu()
                )
                scheduled_time = None
            return

        waiting_entry = None
        for entry in waiting_for_message:
            if entry[0] == ADMIN_ID:
                waiting_entry = entry
                break

        if waiting_entry and str(waiting_entry[1]).startswith("reply_"):
            waiting_for_message.discard(waiting_entry)
            uid = int(str(waiting_entry[1]).split("_")[1])
            if uid not in silenced_users:
                try:
                    await context.bot.send_message(
                        chat_id=uid,
                        text=f"📩 جواب:\n\n{message.text}"
                    )
                    await message.reply_text("✅ جواب ارسال شد!", reply_markup=admin_menu())
                except:
                    await message.reply_text("❌ نتونستم پیام رو بفرستم!", reply_markup=admin_menu())
            else:
                await message.reply_text("🔇 این کاربر سایلنته!", reply_markup=admin_menu())
            return

        if message.reply_to_message:
            for uid, data in user_sessions.items():
                if data['msg_id'] == message.reply_to_message.message_id:
                    if uid not in silenced_users:
                        await context.bot.send_message(chat_id=uid, text=f"📩 جواب:\n\n{message.text}")
                    await message.reply_text("✅ جواب ارسال شد!")
                    return

        await message.reply_text("از پنل مدیریت استفاده کن 👇", reply_markup=admin_menu())
        return

    waiting_entry = None
    for entry in waiting_for_message:
        if entry[0] == user.id:
            waiting_entry = entry
            break

    if waiting_entry:
        waiting_for_message.discard(waiting_entry)
        msg_type = waiting_entry[1]
        name = user.full_name or "ناشناس"
        username = f"@{user.username}" if user.username else "ندارد"
        vip_badge = "⭐ " if user.id in vip_users else ""

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📢 پست در کانال", callback_data=f"post_{user.id}"),
                InlineKeyboardButton("✏️ جواب", callback_data=f"reply_{user.id}")
            ],
            [
                InlineKeyboardButton("🚫 بلاک", callback_data=f"block_{user.id}"),
                InlineKeyboardButton("🔇 سایلنت", callback_data=f"silence_{user.id}")
            ],
            [
                InlineKeyboardButton("✅ آنبلاک", callback_data=f"unblock_{user.id}"),
                InlineKeyboardButton("⭐ VIP", callback_data=f"vip_{user.id}")
            ]
        ])

        if msg_type == "text" and message.text:
            sent = await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"📨 پیام جدید:\n\n{message.text}\n\n{vip_badge}👤 نام: {name}\n🔗 یوزر: {username}\n🆔 آیدی: {user.id}",
                reply_markup=keyboard
            )
            user_sessions[user.id] = {'msg_id': sent.message_id, 'text': message.text}

        elif msg_type == "music" and message.text:
            music_requests.append({'music': message.text, 'name': name, 'user_id': user.id})
            sent = await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"🎵 درخواست موزیک:\n\n{message.text}\n\n{vip_badge}👤 نام: {name}\n🔗 یوزر: {username}\n🆔 آیدی: {user.id}",
                reply_markup=keyboard
            )
            user_sessions[user.id] = {'msg_id': sent.message_id, 'text': message.text}

        elif msg_type == "poll" and message.text:
            lines = message.text.strip().split('\n')
            if len(lines) >= 3:
                question = lines[0]
                options = lines[1:][:10]
                await context.bot.send_poll(
                    chat_id=ADMIN_ID,
                    question=f"📊 نظرسنجی ناشناس: {question}",
                    options=options,
                    is_anonymous=True
                )
                sent = await context.bot.send_message(
                    chat_id=ADMIN_ID,
                    text=f"{vip_badge}👤 نام: {name}\n🔗 یوزر: {username}\n🆔 آیدی: {user.id}",
                    reply_markup=keyboard
                )
                user_sessions[user.id] = {'msg_id': sent.message_id, 'text': '📊 نظرسنجی'}
            else:
                await message.reply_text("❌ فرمت اشتباه! سوال و حداقل ۲ گزینه بنویس!")
                return

        await message.reply_text(
            "✅ پیامت ارسال شد!\n\nاگه جواب داشت بهت میگم 😊",
            reply_markup=main_menu(user.id)
        )
        return

    await message.reply_text("از منوی زیر انتخاب کن 👇", reply_markup=main_menu(user.id))


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
        vip_badge = "⭐ " if user.id in vip_users else ""

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📢 پست در کانال", callback_data=f"post_{user.id}"),
                InlineKeyboardButton("✏️ جواب", callback_data=f"reply_{user.id}")
            ],
            [
                InlineKeyboardButton("🚫 بلاک", callback_data=f"block_{user.id}"),
                InlineKeyboardButton("🔇 سایلنت", callback_data=f"silence_{user.id}")
            ],
            [
                InlineKeyboardButton("✅ آنبلاک", callback_data=f"unblock_{user.id}"),
                InlineKeyboardButton("⭐ VIP", callback_data=f"vip_{user.id}")
            ]
        ])

        sent = await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=update.message.photo[-1].file_id,
            caption=f"🖼️ عکس ناشناس:\n\n{vip_badge}👤 نام: {name}\n🔗 یوزر: {username}\n🆔 آیدی: {user.id}",
            reply_markup=keyboard
        )
        user_sessions[user.id] = {'msg_id': sent.message_id, 'text': '🖼️ عکس'}
        await update.message.reply_text(
            "✅ عکست ارسال شد!\n\nاگه جواب داشت بهت میگم 😊",
            reply_markup=main_menu(user.id)
        )


async def unblock_command(update, context):
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        uid = int(context.args[0])
        blocked_users.discard(uid)
        await update.message.reply_text(f"✅ کاربر {uid} آنبلاک شد!")
    except:
        await update.message.reply_text("❌ مثال: /unblock 123456789")


async def vip_command(update, context):
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        uid = int(context.args[0])
        vip_users.add(uid)
        await update.message.reply_text(f"⭐ کاربر {uid} VIP شد!")
    except:
        await update.message.reply_text("❌ مثال: /vip 123456789")


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("unblock", unblock_command))
    app.add_handler(CommandHandler("vip", vip_command))
    app.add_handler(ChatMemberHandler(track_channel_members, ChatMemberHandler.CHAT_MEMBER))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
