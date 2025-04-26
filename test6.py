from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputTextMessageContent, InlineQueryResultArticle

# تنظیمات ربات
api_id = "API_ID"  # جایگزین با api_id خود
api_hash = "API_HASH"  # جایگزین با api_hash خود
bot_token = "BOT_TOKEN"  # جایگزین با توکن ربات

app = Client("inline_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

@app.on_inline_query()
def inline_main_menu(client, inline_query):
    global authorized_user_id
    authorized_user_id = inline_query.from_user.id
    print(authorized_user_id)

    # تعریف کلید با callback_data
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("پاک کردن این تنظیمات", callback_data="clear_menu")]
        ]
    )

    # ارسال تنظیمات اولیه
    inline_query.answer(
        results=[
            InlineQueryResultArticle(
                title="🎮 تنظیمات بازی",
                description="تعداد سوال، زمان و دعوت از دوستان",
                input_message_content=InputTextMessageContent(
                    "🔧 زمان و تعداد و نوع سوالات را مشخص کنید:"
                ),
                reply_markup=keyboard
            )
        ],
        cache_time=1
    )

@app.on_callback_query()
def handle_callback(client, callback_query):
    if callback_query.data == "clear_menu":  # بررسی کلیک روی دکمه پاک کردن
        if callback_query.from_user.id == authorized_user_id:
            callback_query.message.delete()  # حذف پیام
            callback_query.answer("تنظیمات پاک شد!")  # نمایش پیام تأیید
        else:
            callback_query.answer("شما اجازه انجام این کار را ندارید!", show_alert=True)

# اجرای ربات
app.run()