from pyrogram import Client, filters
from pyrogram.types import InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton

app = Client("my_bot", bot_token="8124230199:AAG87vZW4VZSW7QGJBJH1vYmKP5isXLj8hs", api_id=21612565, api_hash="d5c851ae1170ac168f6ac04ad085da12")

@app.on_inline_query()
def inline_query_handler(client, inline_query):
    result = InlineQueryResultArticle(
        title="🎮 شروع بازی دو نفره",
        description="با دوستت یه چالش راه بنداز!",
        input_message_content=InputTextMessageContent("👇 هرکس آماده‌ست کلیک کنه"),
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ آماده‌ام", callback_data="ready"),
                InlineKeyboardButton("❌ فعلاً نه", callback_data="not_ready")
            ]
        ])
    )
    inline_query.answer([result], cache_time=0)


# @app.on_inline_query()
# def inline_query_handler(client, inline_query):
#     result = InlineQueryResultArticle(
#         title="شروع بازی دو نفره 🎮",
#         description="یه بازی دونفره راه بنداز با دوستت",
#         input_message_content=InputTextMessageContent("بازی شروع شد! هرکسی آماده‌ست دکمه رو بزنه👇"),
#         reply_markup=InlineKeyboardMarkup([
#             [InlineKeyboardButton("✅ آماده‌ام", callback_data="ready")],
#             [InlineKeyboardButton("❌ فعلاً نه", callback_data="not_ready")]
#         ])
#     )
#     inline_query.answer([result])
    
@app.on_callback_query()
def handle_click(client, callback_query):
    user = callback_query.from_user
    callback_query.answer(f"{user.first_name} کلیک کرد ✅")
    # اینجا می‌تونی با استفاده از callback_query.message.edit_text وضعیت‌ها رو تغییر بدی


app.run()
