from pyrogram import Client, filters

# تنظیمات و ساخت کلاینت
api_id = "API_ID"  # جایگزین با api_id خود
api_hash = "API_HASH"  # جایگزین با api_hash خود
bot_token = "BOT_TOKEN"  # جایگزین با توکن ربات

app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# متغیر برای ذخیره آی‌دی کاربر مجاز
authorized_user_id = None

@app.on_message(filters.command("start"))
def start(client, message):
    global authorized_user_id
    authorized_user_id = message.from_user.id
    message.reply("شما اکنون مجاز به استفاده از دکمه‌ها هستید!")

# فیلتر سفارشی برای بررسی آی‌دی کاربر
def is_authorized_user(_, __, message):
    return message.from_user.id == authorized_user_id

authorized_filter = filters.create(is_authorized_user)

@app.on_message(authorized_filter & filters.text)
def handle_buttons(client, message):
    message.reply("شما مجاز به استفاده از این دکمه هستید!")

@app.on_message(~authorized_filter & filters.text)
def handle_unauthorized(client, message):
    message.reply("شما مجاز به استفاده از این دکمه نیستید!")

# اجرای ربات
app.run()