import logging
import random
from datetime import datetime
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
waiting_for_reply_uid = None
all_users = set()
music_requests = []
join_count = 0
left_count = 0

MUSIC_GENRES = {
    "🎸 راک": ["Bohemian Rhapsody - Queen", "Hotel California - Eagles", "Stairway to Heaven - Led Zeppelin"],
    "🎤 پاپ": ["شادمهر عقیلی - دوست دارم", "ماکان بند - نگاهم کن", "سینا شعبانخانی - بمون"],
    "🎵 رپ": ["هیچکس - تهران", "صفریک - آدم برفی", "رضا پیشرو - ماه عسل"],
    "🎻 کلاسیک": ["Mozart - Symphony No.40", "Beethoven - Moonlight Sonata", "Bach - Air on G String"],
    "🌍 جهانی": ["Blinding Lights - The Weeknd", "Shape of You - Ed Sheeran", "Stay - Justin Bieber"],
}

MUSIC_FACTS = [
    "🎵 موزیک سرعت ضربان قلب رو تنظیم می‌کنه!",
    "🎵 گوش دادن به موزیک دوپامین ترشح می‌کنه!",
    "🎵 موزیک می‌تونه درد رو کاهش بده!",
    "🎵 نوازندگان دو طرف مغزشون رو همزمان استفاده می‌کنن!",
    "🎵 موزیک به یادگیری بهتر کمک می‌کنه!",
]


async def is_member(context, user_id):
    try:
        member = await context.bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


def main_menu(user_id=None):
    vip = user_id and user_id in vip_users
    keyboard = [
        [InlineKeyboardButton("📨 پیام ناشناس", callback_data="send_msg"),
         InlineKeyboardButton("🖼️ عکس ناشناس", callback_data="send_photo")],
        [InlineKeyboardButton("🎵 درخواست موزیک", callback_data="send_music"),
         InlineKeyboardButton("📊 نظرسنجی", callback_data="send_poll")],
        [InlineKeyboardButton("🎲 موزیک تصادفی", callback_data="random_music"),
         InlineKeyboardButton("🎸 سبک‌های موزیک", callback_data="music_genres")],
        [InlineKeyboardButton("💬 بحث موزیک", callback_data="music_discuss"),
         InlineKeyboardButton("🏆 چارت موزیک", callback_data="music_chart")],
        [InlineKeyboardButton("📢 کانال ما", url=CHANNEL_LINK),
         InlineKeyboardButton("❓ راهنما", callback_data="help")],
    ]
    if vip:
        keyboard.insert(0, [InlineKeyboardButton("⭐ پنل VIP", callback_data="vip_menu")])
    return InlineKeyboardMarkup(keyboard)


def admin_menu():
    keyboard = [
        [InlineKeyboardButton("📊 آمار کامل", callback_data="admin_stats")],
        [InlineKeyboardButton("🎵 درخواست‌های موزیک", callback_data="admin_music"),
         InlineKeyboardButton("💬 بحث‌های اخیر", callback_data="admin_discussions")],
        [InlineKeyboardButton("📢 پیام همگانی", callback_data="admin_broadcast"),
         InlineKeyboardButton("📢 پیام به VIP", callback_data="admin_broadcast_vip")],
        [InlineKeyboardButton("🚫 لیست بلاک", callback_data="admin_blocklist"),
         InlineKeyboardButton("⭐ لیست VIP", callback_data="admin_viplist")],
        [InlineKeyboardButton("🔇 لیست سایلنت", callback_data="admin_silencelist")],
    ]
    return InlineKeyboardMarkup(keyboard)


def back_btn(cb="admin_back"):
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data=cb)]])


async def start(update, context):
    user = update.effective_user
    all_users.add(user.id)

    if user.id == ADMIN_ID:
        await update.message.reply_text(
            f"👑 سلام ادمین!\n\n📊 آمار سریع:\n👥 کاربران: {len(all_users)}\n🟢 جوین امروز: {join_count}\n🔴 لفت امروز: {left_count}\n\nپنل مدیریت:",
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
            "🌪️ سلام!\n\nبرای استفاده از ربات اول عضو کانال ما بشو 👇\n\n🎵 موزیک | 📰 اخبار | 💬 جامعه",
            reply_markup=keyboard
        )
        return

    vip_badge = "⭐ " if user.id in vip_users else ""
    fact = random.choice(MUSIC_FACTS)
    await update.message.reply_text(
        f"🌪️ درود بر {vip_badge}{user.first_name}!\n\n"
        f"{fact}\n\n"
        "اینجا می‌تونی:\n"
        "📨 پیام ناشناس بفرستی\n"
        "🎵 موزیک درخواست بدی\n"
        "💬 درباره موزیک بحث کنی\n"
        "🏆 چارت موزیک ببینی\n\n"
        "از منوی زیر انتخاب کن 👇",
        reply_markup=main_menu(user.id)
    )


async def track_channel_members(update, context):
    global join_count, left_count
    result = update.chat_member
    if not result:
        return

    old_status = result.old_chat_member.status
    new_status = result.new_chat_member.status
    user = result.new_chat_member.user

    if old_status in ["left", "kicked"] and new_status == "member":
        join_count += 1
        all_users.add(user.id)
        name = user.full_name or "ناشناس"
        username = f"@{user.username}" if user.username else "ندارد"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("⭐ VIP کن", callback_data=f"vip_{user.id}"),
             InlineKeyboardButton("🚫 بلاک", callback_data=f"block_{user.id}")]
        ])
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🟢 عضو جدید!\n\n👤 {name}\n🔗 {username}\n🆔 {user.id}\n\n📊 جوین امروز: {join_count} | کل: {len(all_users)}",
            reply_markup=keyboard
        )

    elif old_status == "member" and new_status in ["left", "kicked"]:
        left_count += 1
        name = user.full_name or "ناشناس"
        username = f"@{user.username}" if user.username else "ندارد"
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🔴 عضو لفت داد!\n\n👤 {name}\n🔗 {username}\n🆔 {user.id}\n\n📊 لفت امروز: {left_count}"
        )


async def button_handler(update, context):
    global waiting_for_broadcast, waiting_for_reply_uid
    query = update.callback_query
    user = query.from_user
    await query.answer()

    # ---- چک عضویت ----
    if query.data == "check_join":
        member = await is_member(context, user.id)
        if member:
            fact = random.choice(MUSIC_FACTS)
            vip_badge = "⭐ " if user.id in vip_users else ""
            await query.edit_message_text(
                f"✅ عضویتت تایید شد!\n\n🌪️ درود بر {vip_badge}{user.first_name}!\n\n{fact}\n\nاز منوی زیر انتخاب کن 👇",
                reply_markup=main_menu(user.id)
            )
        else:
            await query.answer("❌ هنوز عضو نشدی!", show_alert=True)
        return

    # ---- منوی کاربر ----
    if query.data == "send_msg":
        if user.id in blocked_users:
            await query.answer("❌ مسدود شده‌اید!", show_alert=True)
            return
        waiting_for_message.add((user.id, "text"))
        await query.edit_message_text("📨 پیامت رو بنویس 👇", reply_markup=back_btn("back"))
        return

    if query.data == "send_photo":
        if user.id in blocked_users:
            await query.answer("❌ مسدود شده‌اید!", show_alert=True)
            return
        waiting_for_message.add((user.id, "photo"))
        await query.edit_message_text("🖼️ عکست رو بفرست 👇", reply_markup=back_btn("back"))
        return

    if query.data == "send_music":
        if user.id in blocked_users:
            await query.answer("❌ مسدود شده‌اید!", show_alert=True)
            return
        waiting_for_message.add((user.id, "music"))
        await query.edit_message_text(
            "🎵 درخواست موزیک:\n\nاسم آهنگ و خواننده رو بنویس 👇\nمثال: شادمهر عقیلی - دوست دارم",
            reply_markup=back_btn("back")
        )
        return

    if query.data == "send_poll":
        if user.id in blocked_users:
            await query.answer("❌ مسدود شده‌اید!", show_alert=True)
            return
        waiting_for_message.add((user.id, "poll"))
        await query.edit_message_text(
            "📊 نظرسنجی بساز:\n\nسوال + گزینه‌ها (هر خط جدا):\n\nمثال:\nبهترین خواننده؟\nشادمهر\nماکان بند\nرضا پیشرو",
            reply_markup=back_btn("back")
        )
        return

    if query.data == "random_music":
        genre = random.choice(list(MUSIC_GENRES.keys()))
        song = random.choice(MUSIC_GENRES[genre])
        await query.edit_message_text(
            f"🎲 موزیک تصادفی برات انتخاب شد!\n\n{genre}\n🎵 {song}\n\nازش خوشت اومد؟",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔀 یکی دیگه", callback_data="random_music")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]
            ])
        )
        return

    if query.data == "music_genres":
        keyboard = [[InlineKeyboardButton(genre, callback_data=f"genre_{i}")] for i, genre in enumerate(MUSIC_GENRES.keys())]
        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back")])
        await query.edit_message_text(
            "🎸 سبک موزیک مورد علاقه‌ات رو انتخاب کن:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    if query.data.startswith("genre_"):
        idx = int(query.data.split("_")[1])
        genre = list(MUSIC_GENRES.keys())[idx]
        songs = MUSIC_GENRES[genre]
        text = f"{genre} - پیشنهادهای ما:\n\n"
        for i, song in enumerate(songs, 1):
            text += f"{i}. 🎵 {song}\n"
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 بازگشت", callback_data="music_genres")]
            ])
        )
        return

    if query.data == "music_discuss":
        waiting_for_message.add((user.id, "discuss"))
        await query.edit_message_text(
            "💬 نظرت رو درباره موزیک بنویس!\n\nمی‌تونی:\n- آهنگ معرفی کنی\n- نقد بنویسی\n- سوال بپرسی\n\nپیامت ناشناس به کانال فرستاده میشه 👇",
            reply_markup=back_btn("back")
        )
        return

    if query.data == "music_chart":
        chart_text = "🏆 چارت موزیک هفته:\n\n"
        all_songs = []
        for songs in MUSIC_GENRES.values():
            all_songs.extend(songs)
        top = random.sample(all_songs, min(5, len(all_songs)))
        for i, song in enumerate(top, 1):
            chart_text += f"{i}. 🎵 {song}\n"
        chart_text += "\n📊 این چارت بر اساس درخواست‌های کاربران هست!"
        await query.edit_message_text(
            chart_text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]
            ])
        )
        return

    if query.data == "vip_menu":
        await query.edit_message_text(
            "⭐ پنل VIP\n\nشما کاربر ویژه هستید!\nپیام‌های شما با اولویت بررسی میشه.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📨 پیام VIP", callback_data="send_msg")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]
            ])
        )
        return

    if query.data == "help":
        await query.edit_message_text(
            "❓ راهنما:\n\n"
            "📨 پیام ناشناس - هر چیزی بفرست\n"
            "🖼️ عکس ناشناس - عکس بفرست\n"
            "🎵 درخواست موزیک - آهنگ درخواست بده\n"
            "📊 نظرسنجی - نظرسنجی بساز\n"
            "🎲 موزیک تصادفی - پیشنهاد بگیر\n"
            "🎸 سبک‌های موزیک - بر اساس سبک\n"
            "💬 بحث موزیک - نظر بده\n"
            "🏆 چارت - برترین‌ها\n\n"
            "🔒 هویت شما کاملاً محفوظه",
            reply_markup=back_btn("back")
        )
        return

    if query.data == "back":
        fact = random.choice(MUSIC_FACTS)
        await query.edit_message_text(
            f"{fact}\n\nاز منوی زیر انتخاب کن 👇",
            reply_markup=main_menu(user.id)
        )
        return

    # ---- منوی ادمین ----
    if query.data == "admin_stats":
        await query.edit_message_text(
            f"📊 آمار کامل:\n\n"
            f"👥 کل کاربران: {len(all_users)}\n"
            f"🟢 جوین امروز: {join_count}\n"
            f"🔴 لفت امروز: {left_count}\n"
            f"⭐ VIP: {len(vip_users)}\n"
            f"🚫 بلاک: {len(blocked_users)}\n"
            f"🔇 سایلنت: {len(silenced_users)}\n"
            f"🎵 درخواست موزیک: {len(music_requests)}\n"
            f"📅 {datetime.now().strftime('%Y/%m/%d %H:%M')}",
            reply_markup=back_btn()
        )
        return

    if query.data == "admin_music":
        if music_requests:
            text = f"🎵 {len(music_requests)} درخواست موزیک:\n\n"
            for i, req in enumerate(music_requests[-10:], 1):
                vip = "⭐" if req.get('user_id') in vip_users else ""
                text += f"{i}. {req['music']} {vip}\n   از: {req['name']}\n\n"
        else:
            text = "🎵 هیچ درخواستی نیست!"
        await query.edit_message_text(text, reply_markup=back_btn())
        return

    if query.data == "admin_discussions":
        await query.edit_message_text(
            "💬 بحث‌های اخیر در کانال ارسال شدن.\nبرای مشاهده کانال رو چک کن!",
            reply_markup=back_btn()
        )
        return

    if query.data == "admin_broadcast":
        waiting_for_broadcast = "all"
        await query.edit_message_text(
            "📢 پیام همگانی رو بنویس:\n\nبرای همه کاربران فرستاده میشه!",
            reply_markup=back_btn()
        )
        return

    if query.data == "admin_broadcast_vip":
        waiting_for_broadcast = "vip"
        await query.edit_message_text(
            "⭐ پیام برای VIP‌ها رو بنویس:",
            reply_markup=back_btn()
        )
        return

    if query.data == "admin_blocklist":
        text = "🚫 لیست بلاک:\n\n" + "\n".join([f"🆔 {uid}" for uid in blocked_users]) if blocked_users else "✅ هیچ کاربری بلاک نشده!"
        await query.edit_message_text(text, reply_markup=back_btn())
        return

    if query.data == "admin_viplist":
        text = "⭐ لیست VIP:\n\n" + "\n".join([f"🆔 {uid}" for uid in vip_users]) if vip_users else "هیچ VIP نداری!"
        await query.edit_message_text(text, reply_markup=back_btn())
        return

    if query.data == "admin_silencelist":
        text = "🔇 لیست سایلنت:\n\n" + "\n".join([f"🆔 {uid}" for uid in silenced_users]) if silenced_users else "هیچ سایلنتی نداری!"
        await query.edit_message_text(text, reply_markup=back_btn())
        return

    if query.data == "admin_back":
        waiting_for_broadcast = False
        waiting_for_reply_uid = None
        await query.edit_message_text(
            f"👑 پنل مدیریت:\n\n📊 کاربران: {len(all_users)} | 🟢 جوین: {join_count} | 🔴 لفت: {left_count}",
            reply_markup=admin_menu()
        )
        return

    # ---- دکمه‌های روی پیام کاربر ----
    if query.data.startswith("post_"):
        uid = int(query.data.split("_")[1])
        data = user_sessions.get(uid)
        if data:
            await context.bot.send_message(chat_id=CHANNEL_ID, text=f"📨 پیام ناشناس:\n\n{data['text']}")
            await query.answer("✅ پست شد!", show_alert=True)
        return

    if query.data.startswith("reply_"):
        uid = int(query.data.split("_")[1])
        waiting_for_reply_uid = uid
        await query.answer("✏️ جوابت رو بنویس!", show_alert=True)
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"✏️ جواب برای کاربر {uid} رو بنویس:")
        return

    if query.data.startswith("block_"):
        uid = int(query.data.split("_")[1])
        blocked_users.add(uid)
        silenced_users.discard(uid)
        await query.answer("🚫 بلاک شد!", show_alert=True)
        await query.edit_message_reply_markup(reply_markup=None)
        return

    if query.data.startswith("unblock_"):
        uid = int(query.data.split("_")[1])
        blocked_users.discard(uid)
        await query.answer("✅ آنبلاک شد!", show_alert=True)
        await query.edit_message_reply_markup(reply_markup=None)
        return

    if query.data.startswith("silence_"):
        uid = int(query.data.split("_")[1])
        silenced_users.add(uid)
        await query.answer("🔇 سایلنت شد!", show_alert=True)
        await query.edit_message_reply_markup(reply_markup=None)
        return

    if query.data.startswith("vip_"):
        uid = int(query.data.split("_")[1])
        vip_users.add(uid)
        await query.answer("⭐ VIP شد!", show_alert=True)
        await query.edit_message_reply_markup(reply_markup=None)
        try:
            await context.bot.send_message(chat_id=uid, text="⭐ تبریک! شما به عنوان کاربر VIP انتخاب شدید!")
        except:
            pass
        return


def make_user_keyboard(uid):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 پست در کانال", callback_data=f"post_{uid}"),
         InlineKeyboardButton("✏️ جواب", callback_data=f"reply_{uid}")],
        [InlineKeyboardButton("🚫 بلاک", callback_data=f"block_{uid}"),
         InlineKeyboardButton("🔇 سایلنت", callback_data=f"silence_{uid}")],
        [InlineKeyboardButton("✅ آنبلاک", callback_data=f"unblock_{uid}"),
         InlineKeyboardButton("⭐ VIP", callback_data=f"vip_{uid}")]
    ])


async def handle_message(update, context):
    global waiting_for_broadcast, waiting_for_reply_uid
    user = update.effective_user
    message = update.message
    all_users.add(user.id)

    if user.id in blocked_users:
        await message.reply_text("❌ شما مسدود شده‌اید.")
        return

    # ---- ادمین ----
    if user.id == ADMIN_ID:
        if waiting_for_broadcast:
            mode = waiting_for_broadcast
            waiting_for_broadcast = False
            targets = vip_users if mode == "vip" else all_users
            sent = 0
            for uid in targets:
                if uid != ADMIN_ID:
                    try:
                        await context.bot.send_message(chat_id=uid, text=f"📢 پیام از کانال:\n\n{message.text}")
                        sent += 1
                    except:
                        pass
            label = "VIP" if mode == "vip" else "همه"
            await message.reply_text(f"✅ پیام به {sent} نفر از {label} ارسال شد!", reply_markup=admin_menu())
            return

        if waiting_for_reply_uid:
            uid = waiting_for_reply_uid
            waiting_for_reply_uid = None
            if uid not in silenced_users:
                try:
                    await context.bot.send_message(chat_id=uid, text=f"📩 جواب:\n\n{message.text}")
                    await message.reply_text("✅ جواب ارسال شد!", reply_markup=admin_menu())
                except:
                    await message.reply_text("❌ نتونستم پیام بفرستم!", reply_markup=admin_menu())
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

    # ---- کاربر ----
    waiting_entry = None
    for entry in waiting_for_message:
        if entry[0] == user.id:
            waiting_entry = entry
            break

    if not waiting_entry:
        await message.reply_text("از منوی زیر انتخاب کن 👇", reply_markup=main_menu(user.id))
        return

    waiting_for_message.discard(waiting_entry)
    msg_type = waiting_entry[1]
    name = user.full_name or "ناشناس"
    username = f"@{user.username}" if user.username else "ندارد"
    vip_badge = "⭐ " if user.id in vip_users else ""
    keyboard = make_user_keyboard(user.id)

    if msg_type == "text" and message.text:
        sent = await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"📨 پیام جدید:\n\n{message.text}\n\n{vip_badge}👤 {name}\n🔗 {username}\n🆔 {user.id}",
            reply_markup=keyboard
        )
        user_sessions[user.id] = {'msg_id': sent.message_id, 'text': message.text}

    elif msg_type == "music" and message.text:
        music_requests.append({'music': message.text, 'name': name, 'user_id': user.id})
        sent = await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🎵 درخواست موزیک:\n\n{message.text}\n\n{vip_badge}👤 {name}\n🔗 {username}\n🆔 {user.id}",
            reply_markup=keyboard
        )
        user_sessions[user.id] = {'msg_id': sent.message_id, 'text': message.text}

    elif msg_type == "discuss" and message.text:
        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=f"💬 بحث موزیک:\n\n{message.text}"
        )
        sent = await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"💬 بحث موزیک:\n\n{message.text}\n\n{vip_badge}👤 {name}\n🔗 {username}\n🆔 {user.id}",
            reply_markup=keyboard
        )
        user_sessions[user.id] = {'msg_id': sent.message_id, 'text': message.text}

    elif msg_type == "poll" and message.text:
        lines = message.text.strip().split('\n')
        if len(lines) >= 3:
            question = lines[0]
            options = lines[1:][:10]
            await context.bot.send_poll(
                chat_id=CHANNEL_ID,
                question=f"📊 {question}",
                options=options,
                is_anonymous=True
            )
            sent = await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"📊 نظرسنجی:\n\n{message.text}\n\n{vip_badge}👤 {name}\n🔗 {username}\n🆔 {user.id}",
                reply_markup=keyboard
            )
            user_sessions[user.id] = {'msg_id': sent.message_id, 'text': '📊 نظرسنجی'}
        else:
            await message.reply_text("❌ فرمت اشتباه! سوال + حداقل ۲ گزینه بنویس!")
            return

    await message.reply_text(
        "✅ پیامت ارسال شد! 🎵\n\nاگه جواب داشت بهت میگم 😊",
        reply_markup=main_menu(user.id)
    )


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

    if not waiting_entry:
        return

    waiting_for_message.discard(waiting_entry)
    name = user.full_name or "ناشناس"
    username = f"@{user.username}" if user.username else "ندارد"
    vip_badge = "⭐ " if user.id in vip_users else ""

    sent = await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=update.message.photo[-1].file_id,
        caption=f"🖼️ عکس ناشناس:\n\n{vip_badge}👤 {name}\n🔗 {username}\n🆔 {user.id}",
        reply_markup=make_user_keyboard(user.id)
    )
    user_sessions[user.id] = {'msg_id': sent.message_id, 'text': '🖼️ عکس'}
    await update.message.reply_text("✅ عکست ارسال شد! 😊", reply_markup=main_menu(user.id))


async def unblock_cmd(update, context):
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        uid = int(context.args[0])
        blocked_users.discard(uid)
        await update.message.reply_text(f"✅ کاربر {uid} آنبلاک شد!")
    except:
        await update.message.reply_text("❌ مثال: /unblock 123456789")


async def vip_cmd(update, context):
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        uid = int(context.args[0])
        vip_users.add(uid)
        await update.message.reply_text(f"⭐ کاربر {uid} VIP شد!")
        await context.bot.send_message(chat_id=uid, text="⭐ تبریک! شما کاربر VIP شدید!")
    except:
        await update.message.reply_text("❌ مثال: /vip 123456789")


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("unblock", unblock_cmd))
    app.add_handler(CommandHandler("vip", vip_cmd))
    app.add_handler(ChatMemberHandler(track_channel_members, ChatMemberHandler.CHAT_MEMBER))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
