from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

# وضعیت کاربران در حافظه موقت
statuses = {}

app = Client("my_bot", bot_token="8124230199:AAG87vZW4VZSW7QGJBJH1vYmKP5isXLj8hs", api_id=21612565, api_hash="d5c851ae1170ac168f6ac04ad085da12")

# تابع ساخت دکمه‌ها
def get_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ آماده‌ام", callback_data="ready"),
            InlineKeyboardButton("⏳ فعلاً نه", callback_data="not_ready")
        ]
    ])

# استارت ربات
@app.on_message(filters.command("start"))
def start(client, message):
    statuses.clear()
    message.reply(
        "سلام! با دوستت این دکمه‌ها رو بزن تا آماده بودن‌تون مشخص بشه:",
        reply_markup=get_keyboard()
    )

# هندل کلیک دکمه‌ها
@app.on_callback_query()
def button_click(client, callback_query: CallbackQuery):
    user = callback_query.from_user
    data = callback_query.data

    if data == "ready":
        statuses[user.id] = "✅ آماده"
    elif data == "not_ready":
        statuses[user.id] = "⏳ هنوز نه"

    # ساخت متن وضعیت همه
    status_text = "📋 وضعیت کاربران:\n"
    for uid, status in statuses.items():
        name = client.get_users(uid).first_name
        status_text += f"• {name}: {status}\n"

    # ادیت پیام اصلی
    callback_query.message.edit_text(
        status_text,
        reply_markup=get_keyboard()
    )

    # جلوگیری از ارور "LOADING"
    callback_query.answer("ثبت شد ✅")

app.run()
