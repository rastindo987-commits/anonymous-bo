# پست به کانال (ادمین)
    if query.data.startswith("post_"):
        uid = int(query.data.split("_")[1])
        data = user_sessions.get(uid)
        if data:
            await context.bot.send_message(
                chat_id=CHANNEL_ID,
                text=f"📨 پیام ناشناس:\n\n{data['text']}"
            )
            await query.edit_message_reply_markup(reply_markup=None)
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text="✅ پیام به کانال پست شد!"
            )
        return

    # بلاک کاربر (ادمین)
    if query.data.startswith("block_"):
        uid = int(query.data.split("_")[1])
        blocked_users.add(uid)
        await query.edit_message_reply_markup(reply_markup=None)
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🚫 کاربر {uid} مسدود شد!"
        )
        return

# ---- هندل پیام‌ها ----
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = update.message

    if user.id in blocked_users:
        await message.reply_text("❌ شما مسدود شده‌اید.")
        return

    # ادمین داره جواب میده
    if user.id == ADMIN_ID:
        if message.reply_to_message:
            for uid, data in user_sessions.items():
                if data['msg_id'] == message.reply_to_message.message_id:
                    await context.bot.send_message(
                        chat_id=uid,
                        text=f"📩 جواب:\n\n{message.text}"
                    )
                    await message.reply_text("✅ جواب ارسال شد!")
                    return
        await message.reply_text("⚠️ روی پیام کاربر Reply کن!")
        return

    # کاربر داره پیام میده
    if user.id in waiting_for_message:
        waiting_for_message.discard(user.id)

        name = user.full_name or "ناشناس"
        username = f"@{user.username}" if user.username else "ندارد"

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 پست در کانال", callback_data=f"post_{user.id}"),
             InlineKeyboardButton("🚫 بلاک", callback_data=f"block_{user.id}")]
        ])

        sent = await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"📨 پیام جدید:\n\n{message.text}\n\n"
                 f"👤 نام: {name}\n"
                 f"🔗 یوزر: {username}\n"
                 f"🆔 آیدی: {user.id}",
            reply_markup=keyboard
        )

        user_sessions[user.id] = {
            'msg_id': sent.message_id,
            'text': message.text
        }

        await message.reply_text(
            "✅ پیامت ارسال شد!\n\nاگه جواب داشت بهت میگم 🥷🏻",
            reply_markup=main_menu()
        )
        return

    await message.reply_text(
        "از منوی زیر انتخاب کن 👇",
        reply_markup=main_menu()
    )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if name == "main":
    main()
