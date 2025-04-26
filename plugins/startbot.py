from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardButton, InlineKeyboardMarkup,CallbackQuery,
    InlineQueryResultArticle, InputTextMessageContent
)

authorized_user_id = None
user_selections = {}
# برای ارسال منوی اصلی با inline query
@Client.on_inline_query()
def inline_main_menu(client, inline_query):
    
    
    global user_selections 
    global authorized_user_id
    
    authorized_user_id = inline_query.from_user.id 
    print(authorized_user_id)
    user_selections={}
    inline_query.answer(
        results=[
            InlineQueryResultArticle(
                title="🎮 تنظیمات بازی",
                description="تعداد سوال، زمان و دعوت از دوستان",
                input_message_content=InputTextMessageContent(
                    "🔧 زمان و تعداد و نوع سوالات را مشخص کنید:"
                ),
                reply_markup=my_start_def_glassButton()
            )
        ],
        cache_time=1
    )

#این قسمت برای اینه که فقط کسی که بازی رو فرستاده بتونه دکمه هارو تایید کنه 

# def is_authorized_user(_, __, message):
#     return message.from_user.id == authorized_user_id

# authorized_filter = filters.create(is_authorized_user)





##################################################################################









# ساخت دکمه‌های بازی
def my_start_def_glassButton():
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("تعداد سوالات", callback_data="numberofQ")
            ],
            [
                InlineKeyboardButton("6", callback_data="numb6"),
                InlineKeyboardButton("8", callback_data="numb8"),
                InlineKeyboardButton("10", callback_data="numb10"),
                InlineKeyboardButton("12", callback_data="numb12"),
                InlineKeyboardButton("15", callback_data="numb15"),
                InlineKeyboardButton("18", callback_data="numb18"),
                InlineKeyboardButton("20", callback_data="numb20")
            ],
            [
                InlineKeyboardButton("زمان پاسخ گویی به هر سوال", callback_data="timeForQ")
            ],
            [
                InlineKeyboardButton("10", callback_data="time10"),
                InlineKeyboardButton("15", callback_data="time15"),
                InlineKeyboardButton("20", callback_data="time20")
            ],
            [
                InlineKeyboardButton("🤝 دعوت از دوستان", switch_inline_query="start_quiz")
            ],
            [
                InlineKeyboardButton("شروع آزمون", callback_data="start_exam")
            ]
        ]
    )
    return keyboard 

# ذخیره انتخاب‌ها و نمایش تیک سبز

#user_id = callback_query.from_user.id
@Client.on_callback_query()
def handle_callback_query(client, callback_query:CallbackQuery):
    
    
    if authorized_user_id ==callback_query.from_user.id:
            
        
        
        if callback_query.data == "start_exam" :
            print(user_selections)
            print(authorized_user_id)
            
    
        
        user_id = callback_query.from_user.id
        data = callback_query.data

        # اگر کاربر هنوز انتخابی نکرده است، یک دیکشنری جدید برای او بسازید
        if user_id not in user_selections:
            user_selections[user_id] = {"number": None, "time": None}

        # بررسی و ذخیره انتخاب‌ها
        if data in ["numb10", "numb15", "numb20","numb6","numb8","numb12","numb18"]:
            user_selections[user_id]["number"] = data
        elif data in ["time10", "time15", "time20"]:
            user_selections[user_id]["time"] = data
        if data in ["time10", "time15", "time20","numb10", "numb15", "numb20","numb6","numb8","numb12","numb18"]:
        # ایجاد دکمه‌های به‌روز شده با علامت تیک
            reply_markup = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        text="تعداد سوالات ✅" if user_selections[user_id]["number"] else "تعداد سوالات",
                        callback_data="numberofQ"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="6 ✅" if user_selections[user_id]["number"] == "numb6" else "6", 
                        callback_data="numb6"
                    ),
                    InlineKeyboardButton(
                        text="8 ✅" if user_selections[user_id]["number"] == "numb8" else "8", 
                        callback_data="numb8"
                    ),
                    InlineKeyboardButton(
                        text="10 ✅" if user_selections[user_id]["number"] == "numb10" else "10", 
                        callback_data="numb10"
                    ),
                    InlineKeyboardButton(
                        text="12 ✅" if user_selections[user_id]["number"] == "numb12" else "12", 
                        callback_data="numb12"
                    ),
                    InlineKeyboardButton(
                        text="15 ✅" if user_selections[user_id]["number"] == "numb15" else "15", 
                        callback_data="numb15"
                    ),
                    InlineKeyboardButton(
                        text="18 ✅" if user_selections[user_id]["number"] == "numb18" else "18", 
                        callback_data="numb18"
                    ),
                    InlineKeyboardButton(
                        text="20 ✅" if user_selections[user_id]["number"] == "numb20" else "20", 
                        callback_data="numb20"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="زمان پاسخ گویی ✅" if user_selections[user_id]["time"] else "زمان پاسخ گویی",
                        callback_data="timeForQ"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="10 ✅" if user_selections[user_id]["time"] == "time10" else "10",
                        callback_data="time10"
                    ),
                    InlineKeyboardButton(
                        text="15 ✅" if user_selections[user_id]["time"] == "time15" else "15",
                        callback_data="time15"
                    ),
                    InlineKeyboardButton(
                        text="20 ✅" if user_selections[user_id]["time"] == "time20" else "20",
                        callback_data="time20"
                    )
                ],
                [
                    InlineKeyboardButton("🤝 دعوت از دوستان", switch_inline_query="start_quiz")
                ],
                [
                    InlineKeyboardButton(text="شروع آزمون", callback_data="start_exam")
                ]
            ])
            
            
            # callback_query.edit_reply_markup(reply_markup=reply_markup)
            callback_query.edit_message_reply_markup(reply_markup=reply_markup)




# from pyrogram import Client , filters
# from pyrogram.types import Message,ReplyKeyboardMarkup,InlineKeyboardButton ,InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent


# from pyrogram import Client, filters
# from pyrogram.types import (
#     InlineKeyboardButton, InlineKeyboardMarkup,
#     InlineQueryResultArticle, InputTextMessageContent
# )

# @Client.on_inline_query()
# def inline_main_menu(client, inline_query):

#     inline_query.answer(
#         results=[
#             InlineQueryResultArticle(
#                 title="🎮 تنظیمات بازی",
#                 description="تعداد سوال، زمان و دعوت از دوستان",
#                 input_message_content=InputTextMessageContent(
#                     "🔧 زمان و تعداد و نوع سوالات را مشخص کنید:"
#                 ),
#                 reply_markup = my_start_def_glassButton(Client , Message)
#             )
#         ],
#         cache_time=1
#     )
    
    
# # @Client.on_message()
# def my_start_def_glassButton(client :Client , message:Message):
#     keyboard = InlineKeyboardMarkup(
#         [
#             [
#                 InlineKeyboardButton("تعداد سوالات", callback_data="numberofQ")
#             ],
#             [
#                 InlineKeyboardButton("10", callback_data="numb10"),
#                 InlineKeyboardButton("15", callback_data="numb15"),
#                 InlineKeyboardButton("20", callback_data="numb20")
#             ],
#             [
#                 InlineKeyboardButton("زمان پاسخ گویی به هر سوال", callback_data="timeForQ")
#             ],
#             [
#                 InlineKeyboardButton("10", callback_data="time10"),
#                 InlineKeyboardButton("15", callback_data="time15"),
#                 InlineKeyboardButton("20", callback_data="time20")
#             ],
#             [
#                 InlineKeyboardButton("🤝 دعوت از دوستان", switch_inline_query="start_quiz")
#             ],
#             [
#                 InlineKeyboardButton("شروع آزمون", callback_data="start_exam")
#             ]
#         ]
#     )
#     return keyboard 



# user_selections = {}

# @Client.on_callback_query()
# def handle_callback_query(client, callback_query):
    
    
#     user_id = callback_query.from_user.id
#     data = callback_query.data

#     # اگر کاربر هنوز انتخابی نکرده است، یک دیکشنری جدید برای او بسازید
#     if user_id not in user_selections:
#         user_selections[user_id] = {"number": None, "time": None}

#     # بررسی و ذخیره انتخاب‌ها
#     if data in ["numb10", "numb15", "numb20"]:
#         user_selections[user_id]["number"] = data
#     elif data in ["time10", "time15", "time20"]:
#         user_selections[user_id]["time"] = data

#     # ایجاد دکمه‌های به‌روز شده با علامت تیک
#     reply_markup = InlineKeyboardMarkup([
#         [
#             InlineKeyboardButton(text="تعداد سوالات ✅" if user_selections[user_id]["number"] else "تعداد سوالات",
#                                  callback_data="numberofQ")
#         ],
#         [
#             InlineKeyboardButton(text="10 ✅" if user_selections[user_id]["number"] == "numb10" else "10",
#                                  callback_data="numb10"),
#             InlineKeyboardButton(text="15 ✅" if user_selections[user_id]["number"] == "numb15" else "15",
#                                  callback_data="numb15"),
#             InlineKeyboardButton(text="20 ✅" if user_selections[user_id]["number"] == "numb20" else "20",
#                                  callback_data="numb20")
#         ],
#         [
#             InlineKeyboardButton(text="زمان پاسخ گویی ✅" if user_selections[user_id]["time"] else "زمان پاسخ گویی",
#                                  callback_data="timeForQ")
#         ],
#         [
#             InlineKeyboardButton(text="10 ✅" if user_selections[user_id]["time"] == "time10" else "10",
#                                  callback_data="time10"),
#             InlineKeyboardButton(text="15 ✅" if user_selections[user_id]["time"] == "time15" else "15",
#                                  callback_data="time15"),
#             InlineKeyboardButton(text="20 ✅" if user_selections[user_id]["time"] == "time20" else "20",
#                                  callback_data="time20")
#         ],
#         [
#            InlineKeyboardButton(text="دعوت از دوستان",callback_data="shareWithFriend") 
#         ],
#         [
#                 InlineKeyboardButton(text="شروع آزمون",callback_data="start_exam")
#         ]
#     ])

#     # به‌روز‌رسانی پیام اصلی
#     # callback_query.message.edit_reply_markup(keyboard=reply_markup)
#     # callback_query.edit_inline_message_id(reply_markup=reply_markup)
#     client.edit_message_reply_markup(inline_message_id=callback_query.inline_message_id,reply_markup=reply_markup)

    
    
    
    
    
    
    


# @Client.on_inline_query()
# async def inline_query_handler(client, inline_query):
#     if inline_query.query == "start_quiz":
#         keyboard = InlineKeyboardMarkup(
#             [[InlineKeyboardButton("🎯 شروع بازی", callback_data="start_quiz_game")]]
#         )

#         await inline_query.answer(
#             results=[
#                 InlineQueryResultArticle(
#                     title="دعوت به بازی 🎮",
#                     description="روی این پیام کلیک کن و بازی رو شروع کن!",
#                     input_message_content=InputTextMessageContent(
#                         "🎮 بیا بازی کنیم!\nبرای شروع روی دکمه پایین بزن."
#                     ),
#                     reply_markup=keyboard
#                 )
#             ],
#             cache_time=1
#         )  
# @Client.on_callback_query()
# async def start_quiz(client, callback_query):
#     question_keyboard = InlineKeyboardMarkup(
#         [
#             [InlineKeyboardButton("1️⃣ پاریس", callback_data="answer_1"),
#              InlineKeyboardButton("2️⃣ لندن", callback_data="answer_2")]
#         ]
#     )

#     await callback_query.message.edit_text(
#         "❓ سوال اول: پایتخت فرانسه کجاست؟",
#         reply_markup=question_keyboard
#     )
#     await callback_query.answer("سوال اول!", show_alert=False)
    
# @Client.on_callback_query(filters.regex("answer_"))
# async def answer_handler(client, callback_query):
#     data = callback_query.data
#     if data == "answer_1":
#         await callback_query.answer("✅ درست گفتی!", show_alert=True)
#     else:
#         await callback_query.answer("❌ اشتباهه!", show_alert=True)
# @Client.on_inline_query()
# def inline_query_handler(client, inline_query):
#     inline_query.answer(
#         results=[
#             InlineQueryResultArticle(
#                 title="چالش با دوستت 🎮",
#                 description="دوستت رو دعوت کن به بازی و رقابت",
#                 input_message_content=InputTextMessageContent(
#                     message_text="🎮 بیا با من یه چالش شروع کن!\nبرای بازی روی /start کلیک کن یا به ربات پیام بده."
#                 ),
#                 thumb_url="https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/TG-Icon.png/240px-TG-Icon.png"
#             )
#         ],
#         cache_time=1
#     )

