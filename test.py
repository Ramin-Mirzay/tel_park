# ذخیره وضعیت انتخاب شده‌ها
user_selections = {}

@Client.on_callback_query()
def handle_callback_query(client, callback_query):
    user_id = callback_query.from_user.id
    data = callback_query.data

    # اگر کاربر هنوز انتخابی نکرده است، یک دیکشنری جدید برای او بسازید
    if user_id not in user_selections:
        user_selections[user_id] = {"number": None, "time": None}

    # بررسی و ذخیره انتخاب‌ها
    if data in ["numb10", "numb15", "numb20"]:
        user_selections[user_id]["number"] = data
    elif data in ["time10", "time15", "time20"]:
        user_selections[user_id]["time"] = data

    # ایجاد دکمه‌های به‌روز شده با علامت تیک
    reply_markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(text="تعداد سوالات ✅" if user_selections[user_id]["number"] else "تعداد سوالات",
                                 callback_data="numberofQ")
        ],
        [
            InlineKeyboardButton(text="10 ✅" if user_selections[user_id]["number"] == "numb10" else "10",
                                 callback_data="numb10"),
            InlineKeyboardButton(text="15 ✅" if user_selections[user_id]["number"] == "numb15" else "15",
                                 callback_data="numb15"),
            InlineKeyboardButton(text="20 ✅" if user_selections[user_id]["number"] == "numb20" else "20",
                                 callback_data="numb20")
        ],
        [
            InlineKeyboardButton(text="زمان پاسخ گویی ✅" if user_selections[user_id]["time"] else "زمان پاسخ گویی",
                                 callback_data="timeForQ")
        ],
        [
            InlineKeyboardButton(text="10 ✅" if user_selections[user_id]["time"] == "time10" else "10",
                                 callback_data="time10"),
            InlineKeyboardButton(text="15 ✅" if user_selections[user_id]["time"] == "time15" else "15",
                                 callback_data="time15"),
            InlineKeyboardButton(text="20 ✅" if user_selections[user_id]["time"] == "time20" else "20",
                                 callback_data="time20")
        ]
    ])

    # به‌روز‌رسانی پیام اصلی
    callback_query.message.edit_reply_markup(reply_markup=reply_markup)