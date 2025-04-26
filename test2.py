from pyrogram.types import InlineQueryResultArticle, InputTextMessageContent

@app.on_inline_query()
async def inline_query_handler(client, inline_query):
    await inline_query.answer(
        results=[
            InlineQueryResultArticle(
                title="چالش با دوستت 🎮",
                description="دوستت رو دعوت کن به بازی و رقابت",
                input_message_content=InputTextMessageContent(
                    message_text="🎮 بیا با من یه چالش شروع کن!\nبرای بازی روی /start کلیک کن یا به ربات پیام بده."
                ),
                thumb_url="https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/TG-Icon.png/240px-TG-Icon.png"
            )
        ],
        cache_time=1
    )
