Rastin:
import logging
import random
import json
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, CallbackQueryHandler, filters, ChatMemberHandler

BOT_TOKEN = "8348876985:AAHeUsnnvlAyCyQX4jhxTMGucPzcxBxKss4"
CHANNEL_ID = "@Craaaazyhouse"
CHANNEL_LINK = "https://t.me/Craaaazyhouse"
ADMIN_ID = 1233167568
DATA_FILE = "data.json"

logging.basicConfig(level=logging.INFO)

# ---- ذخیره و بارگذاری داده ----
def load_data():
    global all_users, blocked_users, silenced_users, vip_users, music_requests, join_count, left_count
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
            all_users = set(data.get("all_users", []))
            blocked_users = set(data.get("blocked_users", []))
            silenced_users = set(data.get("silenced_users", []))
            vip_users = set(data.get("vip_users", []))
            music_requests = data.get("music_requests", [])
            join_count = data.get("join_count", 0)
            left_count = data.get("left_count", 0)
        except:
            pass

def save_data():
    try:
        with open(DATA_FILE, "w") as f:
            json.dump({
                "all_users": list(all_users),
                "blocked_users": list(blocked_users),
                "silenced_users": list(silenced_users),
                "vip_users": list(vip_users),
                "music_requests": music_requests,
                "join_count": join_count,
                "left_count": left_count,
            }, f)
    except:
        pass

user_sessions = {}
waiting_for_message = set()
waiting_for_broadcast = False
waiting_for_reply_uid = None
all_users = set()
blocked_users = set()
silenced_users = set()
vip_users = set()
music_requests = []
join_count = 0
left_count = 0

load_data()

MUSIC_GENRES = {
    "🎸 راک": ["Bohemian Rhapsody - Queen", "Hotel California - Eagles", "Stairway to Heaven - Led Zeppelin"],
    "🎤 پاپ": ["شادمهر عقیلی - دوست دارم", "ماکان بند - نگاهم کن", "سینا شعبانخانی - بمون"],
    "🎵 رپ": ["هیچکس - تهران", "صفریک - آدم برفی", "رضا پیشرو - ماه عسل"],
    "🎻 کلاسیک": ["Mozart - Symphony No.40", "Beethoven - Moonlight Sonata", "Bach - Air on G String"],
    "🌍 جهانی": ["Blinding Lights - The Weeknd", "Shape of You - Ed Sheeran", "Stay - Justin Bieber"],
}

RIDDLES = [
    {"q": "چیزیه که هر چقدر بیشتر ازش بکشی، بزرگتر میشه؟", "a": "چاه!"},
    {"q": "همیشه جلوته ولی نمیتونی ببینیش چیه؟", "a": "آینده!"},
    {"q": "چیزیه که دندون داره ولی نمیتونه گاز بگیره؟", "a": "شانه!"},
    {"q": "هر چه بیشتر خشک بشه، بیشتر خیس میکنه؟", "a": "حوله!"},
    {"q": "چیزیه که بدون پا میدوه؟", "a": "رودخونه!"},
]

JOKES = [
    "معلم: چرا دیر اومدی؟\nشاگرد: تابلوی سرعت نوشته بود ۴۰، منم ۴۰ دقیقه صبر کردم! 😂",
    "دکتر: چقدر سیگار میکشی؟\nبیمار: روزی یه نخ\nدکتر: این که چیزی نیست!\nبیمار: آخه کبریت ندارم! 😂",
    "بچه به باباش: بابا معنی WiFi چیه؟\nبابا: نمیدونم\nبچه: پس چرا پسورد نمیدی؟ 😂",
]

SHAMSI_MONTHS = ["فروردین","اردیبهشت","خرداد","تیر","مرداد","شهریور","مهر","آبان","آذر","دی","بهمن","اسفند"]
QAMARI_MONTHS = ["محرم","صفر","ربیع‌الاول","ربیع‌الثانی","جمادی‌الاول","جمادی‌الثانی","رجب","شعبان","رمضان","شوال","ذی‌القعده","ذی‌الحجه"]
DAYS_FA = ["دوشنبه","سه‌شنبه","چهارشنبه","پنج‌شنبه","جمعه","شنبه","یکشنبه"]

OCCASIONS = {
    (1,1): "🎉 نوروز", (1,13): "🌿 سیزده به در",
    (3,1): "🌹 روز مادر", (3,14): "👨‍👧 روز پدر",
    (12,29): "🕯️ شب یلدا (تقریبی)",
}

def get_shamsi_date():
    now = datetime.now()
    g_y, g_m, g_d = now.year, now.month, now.day
    jy = g_y - 1600
    jm = g_m - 1
    jd = g_d - 1
    g_day_no = 365*jy + (jy+3)//4 - (jy+99)//100 + (jy+399)//400
    for i in range(jm):
        g_day_no += [31,28+(1 if (g_y%4==0 and g_y%100!=0) or g_y%400==0 else 0),31,30,31,30,31,31,30,31,30,31][i]
    g_day_no += jd - 1
    j_day_no = g_day_no - 79
    j_np = j_day_no // 12053
    j_day_no %= 12053
    jy = 979 + 33*j_np + 4*(j_day_no//1461)
    j_day_no %= 1461
    if j_day_no

>= 366:
        jy += (j_day_no-1)//365
        j_day_no = (j_day_no-1)%365
    jm = 12
    for i in range(11):
        j_mi = [31,31,31,31,31,31,30,30,30,30,30,29][i]
        if j_day_no >= j_mi:
            j_day_no -= j_mi
        else:
            jm = i+1
            break
    jd = j_day_no + 1
    day_name = DAYS_FA[now.weekday()]
    occasion = OCCASIONS.get((jm, jd), "")
    return jy, jm, jd, day_name, occasion

def get_qamari_date():
    now = datetime.now()
    jd = now.day + (now.month-1)*30
    qm = (jd//29)%12
    qd = jd%29+1
    return qd, QAMARI_MONTHS[qm]


async def is_member(context, user_id):
    try:
        member = await context.bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


def main_menu(user_id=None):
    keyboard = [
        [InlineKeyboardButton("📨 ارسال ناشناس", callback_data="send_anon")],
        [InlineKeyboardButton("🌙 بیشتر", callback_data="more_menu")],
        [InlineKeyboardButton("📢 کانال ما", url=CHANNEL_LINK),
         InlineKeyboardButton("❓ راهنما", callback_data="help")],
    ]
    if user_id and user_id in vip_users:
        keyboard.insert(0, [InlineKeyboardButton("⭐ VIP", callback_data="vip_menu")])
    return InlineKeyboardMarkup(keyboard)


def more_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎵 موزیک", callback_data="music_menu"),
         InlineKeyboardButton("🎭 سرگرمی", callback_data="fun_menu")],
        [InlineKeyboardButton("📅 تقویم", callback_data="calendar"),
         InlineKeyboardButton("📊 نظرسنجی", callback_data="send_poll")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back")],
    ])


def music_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎵 درخواست موزیک", callback_data="send_music")],
        [InlineKeyboardButton("🎲 تصادفی", callback_data="random_music"),
         InlineKeyboardButton("🎸 سبک‌ها", callback_data="music_genres")],
        [InlineKeyboardButton("🏆 چارت", callback_data="music_chart"),
         InlineKeyboardButton("💬 بحث", callback_data="music_discuss")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="more_menu")],
    ])


def fun_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🧩 معما", callback_data="riddle"),
         InlineKeyboardButton("😂 جوک", callback_data="joke")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="more_menu")],
    ])


def admin_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 آمار", callback_data="admin_stats")],
        [InlineKeyboardButton("🎵 درخواست‌های موزیک", callback_data="admin_music")],
        [InlineKeyboardButton("📢 پیام همگانی", callback_data="admin_broadcast"),
         InlineKeyboardButton("⭐ پیام VIP", callback_data="admin_broadcast_vip")],
        [InlineKeyboardButton("🚫 لیست بلاک", callback_data="admin_blocklist"),
         InlineKeyboardButton("⭐ لیست VIP", callback_data="admin_viplist")],
        [InlineKeyboardButton("🔇 لیست سایلنت", callback_data="admin_silencelist")],
    ])


def back_btn(cb="admin_back"):
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data=cb)]])


def make_user_keyboard(uid):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ جواب", callback_data=f"reply_{uid}"),
         InlineKeyboardButton("📢 پست کانال", callback_data=f"post_{uid}")],
        [InlineKeyboardButton("🚫 بلاک", callback_data=f"block_{uid}"),
         InlineKeyboardButton("🔇 سایلنت", callback_data=f"silence_{uid}")],
        [InlineKeyboardButton("✅ آنبلاک", callback_data=f"unblock_{uid}"),
         InlineKeyboardButton("⭐ VIP", callback_data=f"vip_{uid}")]
    ])


async def start(update, context):
    user = update.effective_user
    all_users.add(user.id)
    save_data()

    if user.id == ADMIN_ID:
        await update.message.reply_text(
            f"👑 سلام ادمین!\n📊 کاربران ربات: {len(all_users)} | 🟢 جوین: {join_count} | 🔴 لفت: {left_count}",
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
            "🌪️ سلام!\n\nبرای استفاده از ربات اول عضو کانال ما بشو 👇",
            reply_markup=keyboard
        )
        return

    vip_badge = "⭐ " if user.id in vip_users else ""
    await update.message.reply_text(
        f"🌪️ درود بر {vip_badge}{user.first_name}!\n\n"
        "اینجا می‌تونی ناشناس پیام، عکس، ویدیو و استیکر بفرستی ⚡\n\n"
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
        save_data()
        name = user.full_name or "ناشناس"
        username = f"@{user.username}" if user.username else "ندارد"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("⭐ VIP", callback_data=f"vip_{user.id}"),
             InlineKeyboardButton("🚫 بلاک", callback_data=f"block_{user.id}")]
        ])
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🟢 عضو جدید!\n👤 {name}\n🔗 {username}\n🆔 {user.id}\n📊 جوین: {join_count} | کل: {len(all_users)}",
            reply_markup=keyboard
        )
    elif old_status == "member" and new_status in ["left", "kicked"]:
        left_count += 1
        save_data()
        name = user.full_name or "ناشناس"
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🔴 لفت داد: {name} | لفت: {left_count}"
        )


async def button_handler(update, context):
    global waiting_for_broadcast, waiting_for_reply_uid
    query = update.callback_query
    user = query.from_user
    await query.answer()

    if query.data == "check_join":
        member = await is_member(context, user.id)
        if member:
            vip_badge = "⭐ " if user.id in vip_users else ""
            await query.edit_message_text(
                f"✅ عضویتت تایید شد!\n\n🌪️ درود بر {vip_badge}{user.first_name}!\n\nاز منوی زیر انتخاب کن 👇",
                reply_markup=main_menu(user.id)
            )
        else:
            await query.answer("❌ هنوز عضو نشدی!", show_alert=True)
        return

    if query.data == "send_anon":
        if user.id in blocked_users:
            await query.answer("❌ مسدود شده‌اید!", show_alert=True)
            return
        waiting_for_message.add((user.id, "anon"))
        await query.edit_message_text(
            "📨 پیامت رو بفرست:\n\n✅ متن | ✅ عکس | ✅ ویدیو | ✅ استیکر | ✅ گیف\n\nهر چیزی که میخوای ناشناس بفرست 👇",
            reply_markup=back_btn("back")
        )
        return

    if query.data == "more_menu":
        await query.edit_message_text("🌙 بیشتر:", reply_markup=more_menu())
        return

    if query.data == "music_menu":
        await query.edit_message_text("🎵 موزیک:", reply_markup=music_menu())
        return

    if query.data == "fun_menu":
        await query.edit_message_text("🎭 سرگرمی:", reply_markup=fun_menu())
        return

    if query.data == "send_music":
        if user.id in blocked_users:
            await query.answer("❌ مسدود شده‌اید!", show_alert=True)
            return
        waiting_for_message.add((user.id, "music"))
        await query.edit_message_text(
            "🎵 درخواست موزیک:\nاسم آهنگ و خواننده رو بنویس 👇",
            reply_markup=back_btn("music_menu")
        )
        return

    if query.data == "send_poll":
        if user.id in blocked_users:

await query.answer("❌ مسدود شده‌اید!", show_alert=True)
            return
        waiting_for_message.add((user.id, "poll"))
        await query.edit_message_text(
            "📊 نظرسنجی:\nسوال + گزینه‌ها (هر خط جدا):\n\nمثال:\nبهترین خواننده؟\nشادمهر\nماکان بند",
            reply_markup=back_btn("more_menu")
        )
        return

    if query.data == "random_music":
        genre = random.choice(list(MUSIC_GENRES.keys()))
        song = random.choice(MUSIC_GENRES[genre])
        await query.edit_message_text(
            f"🎲 موزیک تصادفی:\n\n{genre}\n🎵 {song}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔀 یکی دیگه", callback_data="random_music")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="music_menu")]
            ])
        )
        return

    if query.data == "music_genres":
        keyboard = [[InlineKeyboardButton(g, callback_data=f"genre_{i}")] for i, g in enumerate(MUSIC_GENRES.keys())]
        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="music_menu")])
        await query.edit_message_text("🎸 سبک موزیک:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if query.data.startswith("genre_"):
        idx = int(query.data.split("_")[1])
        genre = list(MUSIC_GENRES.keys())[idx]
        songs = MUSIC_GENRES[genre]
        text = f"{genre}:\n\n" + "\n".join([f"{i}. 🎵 {s}" for i, s in enumerate(songs, 1)])
        await query.edit_message_text(text, reply_markup=back_btn("music_genres"))
        return

    if query.data == "music_chart":
        all_songs = [s for songs in MUSIC_GENRES.values() for s in songs]
        top = random.sample(all_songs, min(5, len(all_songs)))
        text = "🏆 چارت:\n\n" + "\n".join([f"{i}. 🎵 {s}" for i, s in enumerate(top, 1)])
        await query.edit_message_text(text, reply_markup=back_btn("music_menu"))
        return

    if query.data == "music_discuss":
        waiting_for_message.add((user.id, "discuss"))
        await query.edit_message_text(
            "💬 نظرت درباره موزیک:\nناشناس به کانال فرستاده میشه 👇",
            reply_markup=back_btn("music_menu")
        )
        return

    if query.data == "calendar":
        jy, jm, jd, day_name, occasion = get_shamsi_date()
        qd, qmonth = get_qamari_date()
        miladi = datetime.now().strftime("%Y/%m/%d")
        text = (
            f"📅 تقویم امروز:\n\n"
            f"🌙 شمسی: {day_name} {jd} {SHAMSI_MONTHS[jm-1]} {jy}\n"
            f"🕌 قمری: {qd} {qmonth}\n"
            f"🌍 میلادی: {miladi}"
        )
        if occasion:
            text += f"\n\n🎉 مناسبت: {occasion}"
        await query.edit_message_text(text, reply_markup=back_btn("more_menu"))
        return

    if query.data == "riddle":
        riddle = random.choice(RIDDLES)
        idx = RIDDLES.index(riddle)
        await query.edit_message_text(
            f"🧩 معما:\n\n❓ {riddle['q']}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💡 جواب", callback_data=f"riddle_ans_{idx}")],
                [InlineKeyboardButton("🔀 معمای دیگه", callback_data="riddle")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="fun_menu")]
            ])
        )
        return

    if query.data.startswith("riddle_ans_"):
        idx = int(query.data.split("_")[2])
        riddle = RIDDLES[idx]
        await query.edit_message_text(
            f"🧩 معما:\n\n❓ {riddle['q']}\n\n💡 {riddle['a']}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔀 معمای دیگه", callback_data="riddle")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="fun_menu")]
            ])
        )
        return

    if query.data == "joke":
        joke = random.choice(JOKES)
        await query.edit_message_text(
            f"😂 جوک:\n\n{joke}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔀 جوک دیگه", callback_data="joke")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="fun_menu")]
            ])

)
        return

    if query.data == "vip_menu":
        await query.edit_message_text(
            "⭐ پنل VIP\n\nشما کاربر ویژه هستید!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📨 ارسال ناشناس", callback_data="send_anon")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]
            ])
        )
        return

    if query.data == "help":
        await query.edit_message_text(
            "❓ راهنما:\n\n"
            "📨 ارسال ناشناس - پیام، عکس، ویدیو، استیکر، گیف\n"
            "🌙 بیشتر - موزیک، سرگرمی، تقویم، نظرسنجی\n\n"
            "🔒 هویت شما کاملاً محفوظه\n"
            "✅ وقتی جواب گرفتی، دکمه دیدم رو بزن",
            reply_markup=back_btn("back")
        )
        return

    if query.data == "back":
        await query.edit_message_text(
            "از منوی زیر انتخاب کن 👇",
            reply_markup=main_menu(user.id)
        )
        return

    if query.data.startswith("seen_"):
        admin_msg_id = int(query.data.split("_")[1])
        await query.edit_message_reply_markup(reply_markup=None)
        try:
            await context.bot.send_message(chat_id=ADMIN_ID, text="👁️ پیامت سین شد!")
        except:
            pass
        return

    # ---- پنل ادمین ----
    if query.data == "admin_stats":
        try:
            member_count = await context.bot.get_chat_member_count(CHANNEL_ID)
        except:
            member_count = "نامشخص"
        await query.edit_message_text(
            f"📊 آمار:\n\n"
            f"📢 ممبرهای کانال: {member_count}\n"
            f"🤖 کاربران ربات: {len(all_users)}\n"
            f"🟢 جوین: {join_count}\n"
            f"🔴 لفت: {left_count}\n"
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
            text = f"🎵 {len(music_requests)} درخواست:\n\n"
            for i, req in enumerate(music_requests[-10:], 1):
                vip = "⭐" if req.get('user_id') in vip_users else ""
                text += f"{i}. {req['music']} {vip}\n"
        else:
            text = "🎵 درخواستی نیست!"
        await query.edit_message_text(text, reply_markup=back_btn())
        return

    if query.data == "admin_broadcast":
        waiting_for_broadcast = "all"
        await query.edit_message_text("📢 پیام همگانی رو بنویس:", reply_markup=back_btn())
        return

    if query.data == "admin_broadcast_vip":
        waiting_for_broadcast = "vip"
        await query.edit_message_text("⭐ پیام VIP رو بنویس:", reply_markup=back_btn())
        return

    if query.data == "admin_blocklist":
        text = "🚫 بلاک:\n" + "\n".join([f"🆔 {u}" for u in blocked_users]) if blocked_users else "✅ خالیه!"
        await query.edit_message_text(text, reply_markup=back_btn())
        return

    if query.data == "admin_viplist":
        text = "⭐ VIP:\n" + "\n".join([f"🆔 {u}" for u in vip_users]) if vip_users else "خالیه!"
        await query.edit_message_text(text, reply_markup=back_btn())
        return

    if query.data == "admin_silencelist":
        text = "🔇 سایلنت:\n" + "\n".join([f"🆔 {u}" for u in silenced_users]) if silenced_users else "خالیه!"
        await query.edit_message_text(text, reply_markup=back_btn())
        return

    if query.data == "admin_back":
        waiting_for_broadcast = False
        waiting_for_reply_uid = None
        await query.edit_message_text(
            f"👑 پنل مدیریت:\n📊 کاربران: {len(all_users)} | 🟢 {join_count} | 🔴 {left_count}",
            reply_markup=admin_menu()
        )
        return

    if query.data.startswith("post_"):
        uid = int(query.data.split("_")[1])
        data = user_sessions.get(uid)
        if data and data.get('text'):
            await context.bot.send_message(chat_id=CHANNEL_ID, text=f"📨 پیام ناشناس:\

n\n{data['text']}")
            await query.answer("✅ پست شد!", show_alert=True)
        return

    if query.data.startswith("reply_"):
        uid = int(query.data.split("_")[1])
        waiting_for_reply_uid = uid
        await query.answer("✏️ جوابت رو بنویس!", show_alert=True)
        await context.bot.send_message(chat_id=ADMIN_ID, text="✏️ جوابت رو بنویس:")
        return

    if query.data.startswith("block_"):
        uid = int(query.data.split("_")[1])
        blocked_users.add(uid)
        save_data()
        await query.answer("🚫 بلاک شد!", show_alert=True)
        await query.edit_message_reply_markup(reply_markup=None)
        return

    if query.data.startswith("unblock_"):
        uid = int(query.data.split("_")[1])
        blocked_users.discard(uid)
        save_data()
        await query.answer("✅ آنبلاک شد!", show_alert=True)
        await query.edit_message_reply_markup(reply_markup=None)
        return

    if query.data.startswith("silence_"):
        uid = int(query.data.split("_")[1])
        silenced_users.add(uid)
        save_data()
        await query.answer("🔇 سایلنت شد!", show_alert=True)
        await query.edit_message_reply_markup(reply_markup=None)
        return

    if query.data.startswith("vip_"):
        uid = int(query.data.split("_")[1])
        vip_users.add(uid)
        save_data()
        await query.answer("⭐ VIP شد!", show_alert=True)
        await query.edit_message_reply_markup(reply_markup=None)
        try:
            await context.bot.send_message(chat_id=uid, text="⭐ تبریک! شما کاربر VIP شدید!")
        except:
            pass
        return


async def send_reply_to_user(context, uid, admin_msg_id, message):
    seen_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ دیدم", callback_data=f"seen_{admin_msg_id}")]
    ])
    if message.text:
        await context.bot.send_message(chat_id=uid, text=f"📩 جواب:\n\n{message.text}", reply_markup=seen_keyboard)
    elif message.sticker:
        await context.bot.send_sticker(chat_id=uid, sticker=message.sticker.file_id)
        await context.bot.send_message(chat_id=uid, text="👆 جواب", reply_markup=seen_keyboard)
    elif message.photo:
        await context.bot.send_photo(chat_id=uid, photo=message.photo[-1].file_id, caption="📩 جواب", reply_markup=seen_keyboard)
    elif message.video:
        await context.bot.send_video(chat_id=uid, video=message.video.file_id, caption="📩 جواب", reply_markup=seen_keyboard)
    elif message.animation:
        await context.bot.send_animation(chat_id=uid, animation=message.animation.file_id)
        await context.bot.send_message(chat_id=uid, text="👆 جواب", reply_markup=seen_keyboard)


async def handle_message(update, context):
    global waiting_for_broadcast, waiting_for_reply_uid
    user = update.effective_user
    message = update.message
    all_users.add(user.id)

    if user.id in blocked_users:
        await message.reply_text("❌ شما مسدود شده‌اید.")
        return

    name = user.full_name or "ناشناس"
    username = f"@{user.username}" if user.username else "ندارد"
    vip_badge = "⭐ " if user.id in vip_users else ""

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
                        await context.bot.send_message(chat_id=uid, text=f"📢 پیام:\n\n{message.text}")
                        sent += 1
                    except:
                        pass
            await message.reply_text(f"✅ به {sent} نفر رسید!", reply_markup=admin_menu())
            return

        if waiting_for_reply_uid:
            uid = waiting_for_reply_uid
            waiting_for_reply_uid = None
            if uid not in silenced_users:
                try:
                    admin_msg_id = user_sessions.get(uid, {}).get('msg_id', 0)
                    await send_reply_to_user(cont

ext, uid, admin_msg_id, message)
                    await message.reply_text("✅ جواب ارسال شد!", reply_markup=admin_menu())
                except:
                    await message.reply_text("❌ نتونستم بفرستم!", reply_markup=admin_menu())
            else:
                await message.reply_text("🔇 سایلنته!", reply_markup=admin_menu())
            return

        if message.reply_to_message:
            for uid, data in user_sessions.items():
                if data['msg_id'] == message.reply_to_message.message_id:
                    if uid not in silenced_users:
                        admin_msg_id = data['msg_id']
                        await send_reply_to_user(context, uid, admin_msg_id, message)
                    await message.reply_text("✅ ارسال شد!")
                    return

        await message.reply_text("از پنل استفاده کن 👇", reply_markup=admin_menu())
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
    keyboard = make_user_keyboard(user.id)

    if msg_type == "anon":
        sent = None
        if message.text:
            sent = await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"📨 پیام ناشناس:\n\n{message.text}\n\n{vip_badge}👤 {name}\n🔗 {username}\n🆔 {user.id}",
                reply_markup=keyboard
            )
        elif message.photo:
            sent = await context.bot.send_photo(
                chat_id=ADMIN_ID,
                photo=message.photo[-1].file_id,
                caption=f"🖼️ عکس ناشناس\n\n{vip_badge}👤 {name}\n🔗 {username}\n🆔 {user.id}",
                reply_markup=keyboard
            )
        elif message.video:
            sent = await context.bot.send_video(
                chat_id=ADMIN_ID,
                video=message.video.file_id,
                caption=f"🎥 ویدیو ناشناس\n\n{vip_badge}👤 {name}\n🔗 {username}\n🆔 {user.id}",
                reply_markup=keyboard
            )
        elif message.sticker:
            await context.bot.send_sticker(chat_id=ADMIN_ID, sticker=message.sticker.file_id)
            sent = await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"☝️ استیکر ناشناس\n\n{vip_badge}👤 {name}\n🔗 {username}\n🆔 {user.id}",
                reply_markup=keyboard
            )
        elif message.animation:
            await context.bot.send_animation(chat_id=ADMIN_ID, animation=message.animation.file_id)
            sent = await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"☝️ گیف ناشناس\n\n{vip_badge}👤 {name}\n🔗 {username}\n🆔 {user.id}",
                reply_markup=keyboard
            )

        if sent:
            user_sessions[user.id] = {'msg_id': sent.message_id, 'text': message.text or '📎 فایل'}

    elif msg_type == "music" and message.text:
        music_requests.append({'music': message.text, 'user_id': user.id})
        save_data()
        sent = await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🎵 درخواست موزیک:\n\n{message.text}\n\n{vip_badge}👤 {name}\n🔗 {username}\n🆔 {user.id}",
            reply_markup=keyboard
        )
        user_sessions[user.id] = {'msg_id': sent.message_id, 'text': message.text}

    elif msg_type == "discuss" and message.text:
        await context.bot.send_message(chat_id=CHANNEL_ID, text=f"💬 بحث موزیک:\n\n{message.text}")
        sent = await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"💬 بحث موزیک:\n\n{message.text}\n\n{vip_badge}👤 {name}\n🔗 {username}\n🆔 {user.id}",
            reply_markup=keyboard
        )
        user_sessions[user.id] = {'msg_id': sent.message_id, 'text': message.text}

    elif msg_type == "poll" and message.text:
        lines = message.text.s

trip().split('\n')
        if len(lines) >= 3:
            await context.bot.send_poll(
                chat_id=CHANNEL_ID,
                question=f"📊 {lines[0]}",
                options=lines[1:][:10],
                is_anonymous=True
            )
            sent = await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"📊 نظرسنجی:\n\n{message.text}\n\n{vip_badge}👤 {name}\n🔗 {username}\n🆔 {user.id}",
                reply_markup=keyboard
            )
            user_sessions[user.id] = {'msg_id': sent.message_id, 'text': '📊 نظرسنجی'}
        else:
            await message.reply_text("❌ سوال + حداقل ۲ گزینه بنویس!")
            return

    await message.reply_text("✅ ارسال شد! 😊", reply_markup=main_menu(user.id))


async def unblock_cmd(update, context):
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        uid = int(context.args[0])
        blocked_users.discard(uid)
        save_data()
        await update.message.reply_text(f"✅ آنبلاک شد!")
    except:
        await update.message.reply_text("❌ مثال: /unblock 123456789")


async def vip_cmd(update, context):
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        uid = int(context.args[0])
        vip_users.add(uid)
        save_data()
        await update.message.reply_text(f"⭐ VIP شد!")
        await context.bot.send_message(chat_id=uid, text="⭐ تبریک! VIP شدید!")
    except:
        await update.message.reply_text("❌ مثال: /vip 123456789")


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("unblock", unblock_cmd))
    app.add_handler(CommandHandler("vip", vip_cmd))
    app.add_handler(ChatMemberHandler(track_channel_members, ChatMemberHandler.CHAT_MEMBER))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(
        filters.TEXT | filters.PHOTO | filters.VIDEO | filters.Sticker.ALL | filters.ANIMATION,
        handle_message
    ))
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if name == "main":
    main()
