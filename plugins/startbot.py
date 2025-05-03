import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent, CallbackQuery
import pyrogram

user_selections = {}
game_players = {}         # ذخیره لیست بازیکنان هر بازی
player_choices = {}       # ذخیره انتخاب گزینه بازیکنان

@Client.on_inline_query()
def inline_main_menu(client: Client, inline_query):
    user_id = inline_query.from_user.id
    if user_id not in user_selections:
        user_selections[user_id] = {"number": None, "time": [], "topics": []}

    inline_query.answer(
        results=[
            InlineQueryResultArticle(
                title="🎮 تنظیمات بازی",
                description="تعداد سوال، زمان و دعوت از دوستان",
                input_message_content=InputTextMessageContent("به ربات سوالات خوش آمدید. لطفا تنظیمات بازی را مشخص کنید:"),
                reply_markup=my_start_def_glassButton(user_id)
            )
        ],
        cache_time=1
    )

def my_start_def_glassButton(user_id):
    selections = user_selections.get(user_id, {"number": None, "time": [], "topics": []})
    number = selections["number"]
    times = selections["time"]
    topics = selections["topics"]
    def cb(data): return f"{user_id}|{data}"

    return InlineKeyboardMarkup([
        [InlineKeyboardButton("تعداد سوالات", callback_data=cb("numberofQ"))],
        [*[InlineKeyboardButton(f"{n[4:]} ✅" if number == n else n[4:], callback_data=cb(n))
            for n in ["numb6", "numb8", "numb10", "numb12", "numb15", "numb18", "numb20"]]],
        [InlineKeyboardButton("⏱️ زمان پاسخ", callback_data=cb("timeForQ"))],
        [*[InlineKeyboardButton(t[4:] + (" ✅" if t in times else ""), callback_data=cb(t))
            for t in ["time10", "time15", "time20"]]],
        [InlineKeyboardButton("📚 انتخاب موضوع", callback_data=cb("selectTopic"))],
        [
            InlineKeyboardButton("ریاضی ✅" if "topic_math" in topics else "ریاضی", callback_data=cb("topic_math")),
            InlineKeyboardButton("تاریخ ✅" if "topic_history" in topics else "تاریخ", callback_data=cb("topic_history")),
            InlineKeyboardButton("علمی ✅" if "topic_science" in topics else "علمی", callback_data=cb("topic_science")),
        ],
        [
            InlineKeyboardButton("ادبیات ✅" if "topic_literature" in topics else "ادبیات", callback_data=cb("topic_literature")),
            InlineKeyboardButton("ورزش ✅" if "topic_sports" in topics else "ورزش", callback_data=cb("topic_sports")),
            InlineKeyboardButton("سینما ✅" if "topic_cinema" in topics else "سینما", callback_data=cb("topic_cinema")),
        ],
        [InlineKeyboardButton("🤝 دعوت از دوستان", switch_inline_query="start_quiz")],
        [InlineKeyboardButton("🎮 ساخت بازی", callback_data=cb("start_exam"))]
    ])

@Client.on_callback_query()
async def handle_callback_query(client: Client, callback_query: CallbackQuery):
    from_user = callback_query.from_user
    from_user_id = from_user.id
    data = callback_query.data

    try:
        owner_id_str, pure_data = data.split("|", 1)
        owner_id = int(owner_id_str)
    except ValueError:
        await callback_query.answer("❌ دکمه نامعتبر", show_alert=True)
        return

    if owner_id not in user_selections:
        user_selections[owner_id] = {"number": None, "time": [], "topics": []}

    selections = user_selections[owner_id]
    needs_update = False

    if from_user_id != owner_id and pure_data not in ["ready_now", "option_1", "option_2"]:
        await callback_query.answer("⛔ فقط سازنده بازی می‌تواند تنظیمات را تغییر دهد", show_alert=True)
        return

    if pure_data.startswith("numb"):
        selections["number"] = pure_data
        needs_update = True
    elif pure_data.startswith("time"):
        selections["time"] = [pure_data]
        needs_update = True
    elif pure_data.startswith("topic_"):
        if pure_data in selections["topics"]:
            selections["topics"].remove(pure_data)
        else:
            selections["topics"].append(pure_data)
        needs_update = True

    elif pure_data == "start_exam":
        if not selections["number"] or not selections["time"] or not selections["topics"]:
            await callback_query.answer("لطفاً همه فیلدها را انتخاب کنید ❗", show_alert=True)
            return

        game_players[owner_id] = []
        player_choices[owner_id] = {}

        # ساخت متن پیام همراه با لیست بازیکنان
        players_list = "👥 بازیکنان حاضر:\n" + "\n".join([
            f"👤 {user.first_name}"
            for user_id in game_players.get(owner_id, [])
            if (user := await client.get_users(user_id))  # دریافت اطلاعات کاربر
        ]) if game_players.get(owner_id) else "⏳ هنوز بازیکنی اضافه نشده!"

        await callback_query.edit_message_text(
            f"🎯 لطفاً یکی از گزینه‌ها را انتخاب کنید:\n\n{players_list}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ حاضر", callback_data=f"{owner_id}|ready_now")],
                [InlineKeyboardButton("🚀 شروع", callback_data=f"{owner_id}|start_now")],
                [InlineKeyboardButton("🔙 برگشت به منو", callback_data=f"{owner_id}|back_to_menu")]
            ])
        )
        await callback_query.answer("✅ بازی ساخته شد")
        return


    elif pure_data == "ready_now":

        # اگر کاربر (چه سازنده، چه بازیکن) هنوز در لیست نیست، اضافه شود

        if owner_id in game_players and from_user_id not in game_players[owner_id]:
            game_players[owner_id].append(from_user_id)

            user = await client.get_users(from_user_id)  # دریافت اطلاعات کاربر

            print(f"👤 بازیکن جدید: {user.first_name} (آیدی: {from_user_id}) به بازی اضافه شد.")

        # ساخت متن جدید با لیست بازیکنان

        players_list = "👥 بازیکنان حاضر:\n" + "\n".join([

            f"👤 {(await client.get_users(player_id)).first_name}"

            for player_id in game_players[owner_id]

        ]) if game_players.get(owner_id) else "⏳ هنوز بازیکنی اضافه نشده!"

        try:

            await callback_query.edit_message_text(

                f"🎯 لطفاً یکی از گزینه‌ها را انتخاب کنید:\n\n{players_list}",

                reply_markup=InlineKeyboardMarkup([

                    [InlineKeyboardButton("✅ حاضر", callback_data=f"{owner_id}|ready_now")],

                    [InlineKeyboardButton("🚀 شروع", callback_data=f"{owner_id}|start_now")],

                    [InlineKeyboardButton("🔙 برگشت به منو", callback_data=f"{owner_id}|back_to_menu")]

                ])

            )

        except pyrogram.errors.exceptions.bad_request_400.MessageNotModified:

            pass  # اگر پیام تغییری نکرده، خطا را نادیده بگیر

        await callback_query.answer("✅ شما به لیست بازیکنان اضافه شدید")

        return
    # elif pure_data == "start_exam":
    #     if not selections["number"] or not selections["time"] or not selections["topics"]:
    #         await callback_query.answer("لطفاً همه فیلدها را انتخاب کنید ❗", show_alert=True)
    #         return
    #
    #     game_players[owner_id] = []
    #     player_choices[owner_id] = {}
    #
    #     await callback_query.edit_message_text(
    #         "🎯 لطفاً یکی از گزینه‌ها را انتخاب کنید:",
    #         reply_markup=InlineKeyboardMarkup([
    #             [InlineKeyboardButton("✅ حاضر", callback_data=f"{owner_id}|ready_now")],
    #             [InlineKeyboardButton("🚀 شروع", callback_data=f"{owner_id}|start_now")],
    #             [InlineKeyboardButton("🔙 برگشت به منو", callback_data=f"{owner_id}|back_to_menu")]
    #         ])
    #     )
    #     await callback_query.answer("✅ بازی ساخته شد")
    #     return
    # elif pure_data == "ready_now":
    #     if from_user_id != owner_id:
    #         if owner_id in game_players and from_user_id not in game_players[owner_id]:
    #             game_players[owner_id].append(from_user_id)
    #             # نمایش نام کاربری و آیدی کاربر
    #             user_name = from_user.first_name
    #             if from_user.last_name:
    #                 user_name += " " + from_user.last_name
    #             print(f"👤 بازیکن جدید: {user_name} (آیدی: {from_user_id}) به بازی اضافه شد.")
    #         await callback_query.answer("شما به بازی اضافه شدید ✅")
    #     else:
    #         await callback_query.answer("شما سازنده بازی هستید ✅")
    #     return
    elif pure_data == "start_now":
        time_str = user_selections[owner_id]["time"][0]
        seconds = int(time_str.replace("time", ""))

        await callback_query.edit_message_text(
            f"⏳ بازی شروع شد! شما {seconds} ثانیه وقت دارید یکی از گزینه‌ها را انتخاب کنید:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔵 گزینه 1", callback_data=f"{owner_id}|option_1"),
                 InlineKeyboardButton("🟢 گزینه 2", callback_data=f"{owner_id}|option_2")]
            ])
        )

        await asyncio.sleep(seconds)

        choices = player_choices.get(owner_id, {})
        result_lines = ["📊 نتیجه انتخاب بازیکنان:"]
        for player_id in game_players.get(owner_id, []):
            choice = choices.get(player_id, "❓ انتخاب نشده")
            name = f"[{player_id}](tg://user?id={player_id})"
            symbol = "🔵 گزینه 1" if choice == "option_1" else ("🟢 گزینه 2" if choice == "option_2" else "❓")
            result_lines.append(f"{name}: {symbol}")

        try:
            if callback_query.message:
                await client.edit_message_text(
                    chat_id=callback_query.message.chat.id,
                    message_id=callback_query.message.message_id,
                    text="\n".join(result_lines),
                    disable_web_page_preview=True
                )
            elif callback_query.inline_message_id:
                await client.edit_message_text(
                    inline_message_id=callback_query.inline_message_id,
                    text="\n".join(result_lines),
                    disable_web_page_preview=True
                )
        except Exception as e:
            print("❌ خطا در ویرایش پیام نتایج:", e)

        return
    elif pure_data == "option_1":
        player_choices.setdefault(owner_id, {})[from_user_id] = "option_1"
        await callback_query.answer("🔵 گزینه 1 انتخاب شد")
        return
    elif pure_data == "option_2":
        player_choices.setdefault(owner_id, {})[from_user_id] = "option_2"
        await callback_query.answer("🟢 گزینه 2 انتخاب شد")
        return
    elif pure_data == "back_to_menu":
        await callback_query.edit_message_text(
            "🎮 لطفاً تعداد سوال، زمان و موضوع را انتخاب کنید:",
            reply_markup=my_start_def_glassButton(owner_id)
        )
        await callback_query.answer("🔙 برگشت به منو")
        return

    if needs_update:
        try:
            await callback_query.edit_message_reply_markup(reply_markup=my_start_def_glassButton(owner_id))
            await callback_query.answer("✅ انتخاب تغییر کرد")
        except pyrogram.errors.exceptions.bad_request_400.MessageNotModified:
            pass
    else:
        await callback_query.answer("⚠️ این گزینه از قبل انتخاب شده")

#3333333333333333333333333333333333333333333333333333333333333333
# from pyrogram import Client, filters
# from pyrogram.types import (
#     InlineKeyboardButton, InlineKeyboardMarkup,
#     InlineQueryResultArticle, InputTextMessageContent,
#     CallbackQuery
# )
# import pyrogram
#
# user_selections = {}
# game_players = {}  # ذخیره بازیکنان هر بازی
#
# @Client.on_inline_query()
# def inline_main_menu(client: Client, inline_query):
#     user_id = inline_query.from_user.id
#     if user_id not in user_selections:
#         user_selections[user_id] = {
#             "number": None,
#             "time": [],
#             "topics": []
#         }
#
#     inline_query.answer(
#         results=[
#             InlineQueryResultArticle(
#                 title="🎮 تنظیمات بازی",
#                 description="تعداد سوال، زمان و دعوت از دوستان",
#                 input_message_content=InputTextMessageContent(
#                     "به ربات سوالات خوش آمدید. لطفا تنظیمات بازی را مشخص کنید:"
#                 ),
#                 reply_markup=my_start_def_glassButton(user_id)
#             )
#         ],
#         cache_time=1
#     )
#
# def my_start_def_glassButton(user_id):
#     selections = user_selections.get(user_id, {"number": None, "time": [], "topics": []})
#     number = selections["number"]
#     times = selections["time"]
#     topics = selections["topics"]
#
#     def cb(data): return f"{user_id}|{data}"
#
#     return InlineKeyboardMarkup([
#         [InlineKeyboardButton("تعداد سوالات", callback_data=cb("numberofQ"))],
#         [*[InlineKeyboardButton(f"{n[4:]} ✅" if number == n else n[4:], callback_data=cb(n))
#            for n in ["numb6", "numb8", "numb10", "numb12", "numb15", "numb18", "numb20"]]],
#         [InlineKeyboardButton("⏱️ زمان پاسخ", callback_data=cb("timeForQ"))],
#         [*[InlineKeyboardButton(t[4:] + (" ✅" if t in times else ""), callback_data=cb(t))
#            for t in ["time10", "time15", "time20"]]],
#         [InlineKeyboardButton("📚 انتخاب موضوع", callback_data=cb("selectTopic"))],
#         [
#             InlineKeyboardButton("ریاضی ✅" if "topic_math" in topics else "ریاضی", callback_data=cb("topic_math")),
#             InlineKeyboardButton("تاریخ ✅" if "topic_history" in topics else "تاریخ", callback_data=cb("topic_history")),
#             InlineKeyboardButton("علمی ✅" if "topic_science" in topics else "علمی", callback_data=cb("topic_science")),
#         ],
#         [
#             InlineKeyboardButton("ادبیات ✅" if "topic_literature" in topics else "ادبیات", callback_data=cb("topic_literature")),
#             InlineKeyboardButton("ورزش ✅" if "topic_sports" in topics else "ورزش", callback_data=cb("topic_sports")),
#             InlineKeyboardButton("سینما ✅" if "topic_cinema" in topics else "سینما", callback_data=cb("topic_cinema")),
#         ],
#         [InlineKeyboardButton("🤝 دعوت از دوستان", switch_inline_query="start_quiz")],
#         [InlineKeyboardButton("🎮 ساخت بازی", callback_data=cb("start_exam"))]
#     ])
#
# @Client.on_callback_query()
# def handle_callback_query(client, callback_query: CallbackQuery):
#     from_user = callback_query.from_user
#     from_user_id = from_user.id
#     data = callback_query.data
#
#     try:
#         owner_id_str, pure_data = data.split("|", 1)
#         owner_id = int(owner_id_str)
#     except ValueError:
#         callback_query.answer("❌ دکمه نامعتبر", show_alert=True)
#         return
#
#     if owner_id not in user_selections:
#         user_selections[owner_id] = {"number": None, "time": [], "topics": []}
#
#     selections = user_selections[owner_id]
#     needs_update = False
#
#     if from_user_id != owner_id and pure_data not in ["ready_now", "option_1", "option_2"]:
#         callback_query.answer("⛔ فقط سازنده بازی می‌تواند تنظیمات را تغییر دهد", show_alert=True)
#         return
#
#     if pure_data.startswith("numb"):
#         selections["number"] = pure_data
#         needs_update = True
#     elif pure_data.startswith("time"):
#         selections["time"] = [pure_data]
#         needs_update = True
#     elif pure_data.startswith("topic_"):
#         if pure_data in selections["topics"]:
#             selections["topics"].remove(pure_data)
#         else:
#             selections["topics"].append(pure_data)
#         needs_update = True
#     elif pure_data == "start_exam":
#         if not selections["number"] or not selections["time"] or not selections["topics"]:
#             callback_query.answer("لطفاً همه فیلدها را انتخاب کنید ❗", show_alert=True)
#             return
#
#         first_name = from_user.first_name or ""
#         last_name = from_user.last_name or ""
#         full_name = f"{first_name} {last_name}".strip()
#
#         print(f"\n👤 سازنده بازی: {owner_id} - {full_name}")
#         print(f"🔢 تعداد سوال: {selections['number']}")
#         print(f"⏱️ زمان: {selections['time']}")
#         print(f"📚 موضوعات: {selections['topics']}\n")
#
#         game_players[owner_id] = []  # لیست بازیکنان بازی سازنده
#
#         new_keyboard = InlineKeyboardMarkup([
#             [InlineKeyboardButton("✅ حاضر", callback_data=f"{owner_id}|ready_now")],
#             [InlineKeyboardButton("🚀 شروع", callback_data=f"{owner_id}|start_now")],
#             [InlineKeyboardButton("🔙 برگشت به منو", callback_data=f"{owner_id}|back_to_menu")]
#         ])
#         callback_query.edit_message_text("🎯 لطفاً یکی از گزینه‌ها را انتخاب کنید:", reply_markup=new_keyboard)
#         callback_query.answer("✅ بازی ساخته شد")
#         return
#     elif pure_data == "ready_now":
#         if owner_id in game_players and from_user_id not in game_players[owner_id]:
#             game_players[owner_id].append(from_user_id)
#
#             name = f"{from_user.first_name or ''} {from_user.last_name or ''}".strip()
#             print(f"👥 بازیکن جدید: {name} (ID: {from_user_id}) به بازی کاربر {owner_id} اضافه شد.")
#
#         # ساخت لیست نام بازیکنان
#         player_names = []
#         for pid in game_players[owner_id]:
#             try:
#                 user = client.get_users(pid)
#                 pname = f"{user.first_name or ''} {user.last_name or ''}".strip()
#                 player_names.append(f"• {pname}")
#             except:
#                 continue
#
#         players_text = "\n".join(player_names) if player_names else "هیچ بازیکنی هنوز اضافه نشده است."
#
#         # پیام جدید با نمایش بازیکنان
#         new_text = f"🎯 لطفاً یکی از گزینه‌ها را انتخاب کنید:\n\n👥 بازیکنان حاضر:\n{players_text}"
#
#         new_keyboard = InlineKeyboardMarkup([
#             [InlineKeyboardButton("✅ حاضر", callback_data=f"{owner_id}|ready_now")],
#             [InlineKeyboardButton("🚀 شروع", callback_data=f"{owner_id}|start_now")],
#             [InlineKeyboardButton("🔙 برگشت به منو", callback_data=f"{owner_id}|back_to_menu")]
#         ])
#
#         try:
#             callback_query.edit_message_text(new_text, reply_markup=new_keyboard)
#         except pyrogram.errors.exceptions.bad_request_400.MessageNotModified:
#             pass
#
#         if from_user_id != owner_id:
#             callback_query.answer("شما به بازی اضافه شدید ✅")
#         else:
#             callback_query.answer("شما سازنده بازی هستید ✅")
#         return
#     elif pure_data == "start_now":
#         new_keyboard = InlineKeyboardMarkup([
#             [InlineKeyboardButton("🔵 گزینه 1", callback_data=f"{owner_id}|option_1"),
#              InlineKeyboardButton("🟢 گزینه 2", callback_data=f"{owner_id}|option_2")]
#         ])
#         callback_query.edit_message_text("👑 لطفاً یکی از گزینه‌ها را انتخاب کنید:", reply_markup=new_keyboard)
#         callback_query.answer("✨ بازی شروع شد!")
#         return
#     elif pure_data == "back_to_menu":
#         reply_markup = my_start_def_glassButton(owner_id)
#         callback_query.edit_message_text("🎮 لطفاً تعداد سوال، زمان و موضوع را انتخاب کنید:", reply_markup=reply_markup)
#         callback_query.answer("🔙 برگشت به منو")
#         return
#     elif pure_data == "option_1":
#         callback_query.answer("🔵 گزینه 1 انتخاب شد")
#         return
#     elif pure_data == "option_2":
#         callback_query.answer("🟢 گزینه 2 انتخاب شد")
#         return
#
#     if needs_update:
#         try:
#             reply_markup = my_start_def_glassButton(owner_id)
#             callback_query.edit_message_reply_markup(reply_markup=reply_markup)
#             callback_query.answer("✅ انتخاب تغییر کرد")
#         except pyrogram.errors.exceptions.bad_request_400.MessageNotModified:
#             pass
#     else:
#         callback_query.answer("⚠️ این گزینه از قبل انتخاب شده")
#
#
#
#
#
#
#
# #33333333333333333333333333333333333333333333333333333333333
# # from pyrogram import Client, filters
# # from pyrogram.types import (
# #     InlineKeyboardButton, InlineKeyboardMarkup,
# #     InlineQueryResultArticle, InputTextMessageContent,
# #     CallbackQuery
# # )
# # import pyrogram
# #
# # user_selections = {}
# # game_players = {}  # ذخیره بازیکنان هر بازی
# #
# # @Client.on_inline_query()
# # def inline_main_menu(client: Client, inline_query):
# #     user_id = inline_query.from_user.id
# #     if user_id not in user_selections:
# #         user_selections[user_id] = {
# #             "number": None,
# #             "time": [],
# #             "topics": []
# #         }
# #
# #     inline_query.answer(
# #         results=[
# #             InlineQueryResultArticle(
# #                 title="🎮 تنظیمات بازی",
# #                 description="تعداد سوال، زمان و دعوت از دوستان",
# #                 input_message_content=InputTextMessageContent(
# #                     "به ربات سوالات خوش آمدید. لطفا تنظیمات بازی را مشخص کنید:"
# #                 ),
# #                 reply_markup=my_start_def_glassButton(user_id)
# #             )
# #         ],
# #         cache_time=1
# #     )
# #
# # def my_start_def_glassButton(user_id):
# #     selections = user_selections.get(user_id, {"number": None, "time": [], "topics": []})
# #     number = selections["number"]
# #     times = selections["time"]
# #     topics = selections["topics"]
# #
# #     def cb(data): return f"{user_id}|{data}"
# #
# #     return InlineKeyboardMarkup([
# #         [InlineKeyboardButton("تعداد سوالات", callback_data=cb("numberofQ"))],
# #         [*[
# #             InlineKeyboardButton(f"{n[4:]} ✅" if number == n else n[4:], callback_data=cb(n))
# #             for n in ["numb6", "numb8", "numb10", "numb12", "numb15", "numb18", "numb20"]
# #         ]],
# #         [InlineKeyboardButton("⏱️ زمان پاسخ", callback_data=cb("timeForQ"))],
# #         [*[
# #             InlineKeyboardButton(t[4:] + (" ✅" if t in times else ""), callback_data=cb(t))
# #             for t in ["time10", "time15", "time20"]
# #         ]],
# #         [InlineKeyboardButton("📚 انتخاب موضوع", callback_data=cb("selectTopic"))],
# #         [
# #             InlineKeyboardButton("ریاضی ✅" if "topic_math" in topics else "ریاضی", callback_data=cb("topic_math")),
# #             InlineKeyboardButton("تاریخ ✅" if "topic_history" in topics else "تاریخ", callback_data=cb("topic_history")),
# #             InlineKeyboardButton("علمی ✅" if "topic_science" in topics else "علمی", callback_data=cb("topic_science")),
# #         ],
# #         [
# #             InlineKeyboardButton("ادبیات ✅" if "topic_literature" in topics else "ادبیات", callback_data=cb("topic_literature")),
# #             InlineKeyboardButton("ورزش ✅" if "topic_sports" in topics else "ورزش", callback_data=cb("topic_sports")),
# #             InlineKeyboardButton("سینما ✅" if "topic_cinema" in topics else "سینما", callback_data=cb("topic_cinema")),
# #         ],
# #         [InlineKeyboardButton("🤝 دعوت از دوستان", switch_inline_query="start_quiz")],
# #         [InlineKeyboardButton("🎮 ساخت بازی", callback_data=cb("start_exam"))]
# #     ])
# #
# # @Client.on_callback_query()
# # def handle_callback_query(client, callback_query: CallbackQuery):
# #     from_user = callback_query.from_user
# #     from_user_id = from_user.id
# #     data = callback_query.data
# #
# #     try:
# #         owner_id_str, pure_data = data.split("|", 1)
# #         owner_id = int(owner_id_str)
# #     except ValueError:
# #         callback_query.answer("❌ دکمه نامعتبر", show_alert=True)
# #         return
# #
# #     if owner_id not in user_selections:
# #         user_selections[owner_id] = {"number": None, "time": [], "topics": []}
# #
# #     selections = user_selections[owner_id]
# #     needs_update = False
# #
# #     # اگر کسی غیر از سازنده دکمه‌ای به جز گزینه‌ها و «حاضر» را بزند
# #     if from_user_id != owner_id and pure_data not in ["ready_now", "option_1", "option_2"]:
# #         callback_query.answer("⛔ فقط سازنده بازی می‌تواند تنظیمات را تغییر دهد", show_alert=True)
# #         return
# #
# #     if pure_data.startswith("numb"):
# #         selections["number"] = pure_data
# #         needs_update = True
# #     elif pure_data.startswith("time"):
# #         selections["time"] = [pure_data]
# #         needs_update = True
# #     elif pure_data.startswith("topic_"):
# #         if pure_data in selections["topics"]:
# #             selections["topics"].remove(pure_data)
# #         else:
# #             selections["topics"].append(pure_data)
# #         needs_update = True
# #     elif pure_data == "start_exam":
# #         if not selections["number"] or not selections["time"] or not selections["topics"]:
# #             callback_query.answer("لطفاً همه فیلدها را انتخاب کنید ❗", show_alert=True)
# #             return
# #
# #         first_name = from_user.first_name or ""
# #         last_name = from_user.last_name or ""
# #         full_name = f"{first_name} {last_name}".strip()
# #
# #         print(f"\n👤 سازنده بازی: {owner_id} - {full_name}")
# #         print(f"🔢 تعداد سوال: {selections['number']}")
# #         print(f"⏱️ زمان: {selections['time']}")
# #         print(f"📚 موضوعات: {selections['topics']}\n")
# #
# #         game_players[owner_id] = []  # لیست بازیکنان بازی سازنده
# #
# #         new_keyboard = InlineKeyboardMarkup([
# #             [InlineKeyboardButton("✅ حاضر", callback_data=f"{owner_id}|ready_now")],
# #             [InlineKeyboardButton("🚀 شروع", callback_data=f"{owner_id}|start_now")],
# #             [InlineKeyboardButton("🔙 برگشت به منو", callback_data=f"{owner_id}|back_to_menu")]
# #         ])
# #         callback_query.edit_message_text("🎯 لطفاً یکی از گزینه‌ها را انتخاب کنید:", reply_markup=new_keyboard)
# #         callback_query.answer("✅ بازی ساخته شد")
# #         return
# #     elif pure_data == "ready_now":
# #         if from_user_id != owner_id:
# #             if owner_id in game_players and from_user_id not in game_players[owner_id]:
# #                 game_players[owner_id].append(from_user_id)
# #
# #                 name = f"{from_user.first_name or ''} {from_user.last_name or ''}".strip()
# #                 print(f"👥 بازیکن جدید: {name} (ID: {from_user_id}) به بازی کاربر {owner_id} اضافه شد.")
# #
# #             callback_query.answer("شما به بازی اضافه شدید ✅")
# #         else:
# #             callback_query.answer("شما سازنده بازی هستید ✅")
# #         return
# #     elif pure_data == "start_now":
# #         new_keyboard = InlineKeyboardMarkup([
# #             [InlineKeyboardButton("🔵 گزینه 1", callback_data=f"{owner_id}|option_1"),
# #              InlineKeyboardButton("🟢 گزینه 2", callback_data=f"{owner_id}|option_2")]
# #         ])
# #         callback_query.edit_message_text("👑 لطفاً یکی از گزینه‌ها را انتخاب کنید:", reply_markup=new_keyboard)
# #         callback_query.answer("✨ بازی شروع شد!")
# #         return
# #     elif pure_data == "back_to_menu":
# #         reply_markup = my_start_def_glassButton(owner_id)
# #         callback_query.edit_message_text("🎮 لطفاً تعداد سوال، زمان و موضوع را انتخاب کنید:", reply_markup=reply_markup)
# #         callback_query.answer("🔙 برگشت به منو")
# #         return
# #     elif pure_data == "option_1":
# #         callback_query.answer("🔵 گزینه 1 انتخاب شد")
# #         return
# #     elif pure_data == "option_2":
# #         callback_query.answer("🟢 گزینه 2 انتخاب شد")
# #         return
# #
# #     if needs_update:
# #         try:
# #             reply_markup = my_start_def_glassButton(owner_id)
# #             callback_query.edit_message_reply_markup(reply_markup=reply_markup)
# #             callback_query.answer("✅ انتخاب تغییر کرد")
# #         except pyrogram.errors.exceptions.bad_request_400.MessageNotModified:
# #             pass
# #     else:
# #         callback_query.answer("⚠️ این گزینه از قبل انتخاب شده")
