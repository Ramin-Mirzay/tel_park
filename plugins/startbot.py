import asyncio
import uuid
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, \
    InputTextMessageContent, CallbackQuery
import pyrogram
import sqlite3
import random
import os
from pyrogram.enums import ChatMemberStatus

print("لود پلاگین startbot...")  # دیباگ: تأیید لود پلاگین

# لیست برای ذخیره سوالات استفاده‌شده
used_questions = set()  # استفاده از set برای کارایی بهتر


class Game:
    def __init__(self, owner_id):
        self.game_id = str(uuid.uuid4())
        self.owner_id = owner_id
        self.selections = {"number": None, "time": [], "topics": []}
        self.players = []
        self.choices = {}  # ساختار: {question_number: {user_id: choice}}
        self.created_at = datetime.now()
        self.last_updated = datetime.now()
        self.current_question = 0
        self.questions = []
        self.scores = {}  # ساختار: {user_id: correct_answers_count}

    def update_timestamp(self):
        self.last_updated = datetime.now()

    def is_expired(self, timeout_minutes=30):
        return datetime.now() - self.last_updated > timedelta(minutes=timeout_minutes)

    def get_settings_summary(self):
        number = self.selections["number"][4:] if self.selections["number"] else "انتخاب نشده"
        time = self.selections["time"][0][4:] + " ثانیه" if self.selections["time"] else "انتخاب نشده"
        topics = ", ".join([t[6:].capitalize() for t in self.selections["topics"]]) or "انتخاب نشده"
        return f"📋 تنظیمات:\nسوالات: {number}\nزمان: {time}\nموضوعات: {topics}"

    def get_total_questions(self):
        if not self.selections["number"]:
            return 0
        return int(self.selections["number"][4:])


games = {}
user_cache = {}


def init_leaderboard_db():
    db_path = "plugins/questions.db"
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS leaderboard (
                user_id INTEGER,
                username TEXT,
                correct_answers INTEGER,
                game_date TEXT,
                PRIMARY KEY (user_id, game_date)
            )
        """)
        conn.commit()
        print("جدول leaderboard با موفقیت ایجاد شد.")
        conn.close()
    except Exception as e:
        print(f"خطا در ایجاد جدول leaderboard: {e}")


def save_player_score(user_id, username, correct_answers):
    db_path = "plugins/questions.db"
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        game_date = datetime.now().strftime("%Y-%m-%d")

        cursor.execute("""
            SELECT correct_answers FROM leaderboard
            WHERE user_id = ? AND game_date = ?
        """, (user_id, game_date))
        result = cursor.fetchone()

        if result:
            existing_correct_answers = result[0]
            total_correct_answers = existing_correct_answers + correct_answers
            cursor.execute("""
                UPDATE leaderboard
                SET correct_answers = ?, username = ?
                WHERE user_id = ? AND game_date = ?
            """, (total_correct_answers, username, user_id, game_date))
            print(f"امتیاز بازیکن {username} (ID: {user_id}) به‌روزرسانی شد: {total_correct_answers} پاسخ درست")
        else:
            cursor.execute("""
                INSERT INTO leaderboard (user_id, username, correct_answers, game_date)
                VALUES (?, ?, ?, ?)
            """, (user_id, username, correct_answers, game_date))
            print(f"امتیاز بازیکن {username} (ID: {user_id}) ذخیره شد: {correct_answers} پاسخ درست")

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"خطا در ذخیره/به‌روزرسانی امتیاز بازیکن: {e}")


def get_leaderboard():
    db_path = "plugins/questions.db"
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT username, SUM(correct_answers) as total_correct
            FROM leaderboard
            GROUP BY user_id, username
            ORDER BY total_correct DESC
            LIMIT 10
        """)
        leaderboard = cursor.fetchall()
        print(f"داده‌های رتبه‌بندی: {leaderboard}")  # دیباگ: نمایش داده‌های رتبه‌بندی
        conn.close()
        return leaderboard
    except Exception as e:
        print(f"خطا در دریافت رتبه‌بندی: {e}")
        return []


async def test_channel_access(client):
    try:
        chat = await client.get_chat("@chalesh_yarr")
        print(f"دسترسی به کانال موفق: {chat.title}")
        bot_id = (await client.get_me()).id
        chat_member = await client.get_chat_member("@chalesh_yarr", bot_id)
        print(f"وضعیت ربات در کانال @chalesh_yarr: {chat_member.status}")
        if chat_member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            print("خطا: ربات در کانال @chalesh_yarr ادمین نیست!")
            return False
        return True
    except Exception as e:
        print(f"خطا در دسترسی به کانال @chalesh_yarr: {str(e)}")
        return False


async def start_background_tasks(client):
    print("ثبت تسک‌های پس‌زمینه در پلاگین startbot...")  # دیباگ: تأیید ثبت
    try:
        asyncio.create_task(cleanup_expired_games())
        asyncio.create_task(announce_leaderboard(client))
        print("تسک‌های پس‌زمینه با موفقیت ثبت شدند.")
    except Exception as e:
        print(f"خطا در ثبت تسک‌های پس‌زمینه: {str(e)}")


async def announce_leaderboard(client):
    print("شروع تابع announce_leaderboard...")  # دیباگ: تأیید شروع
    while True:
        try:
            print("چک کردن دسترسی به کانال...")
            if not await test_channel_access(client):
                print("خطا: ربات به کانال @chalesh_yarr دسترسی ندارد یا ادمین نیست.")
                await asyncio.sleep(10)  # برای تست، 10 ثانیه
                continue

            print("دریافت داده‌های رتبه‌بندی...")
            leaderboard = get_leaderboard()
            if leaderboard:
                message_lines = ["🏆 رتبه‌بندی بازیکنان برتر در چالش یار:"]
                for idx, (username, total_correct) in enumerate(leaderboard, 1):
                    message_lines.append(f"{idx}. {username}: {total_correct} پاسخ درست")
                message = "\n".join(message_lines)
                print(f"ارسال پیام به کانال: {message}")
                await client.send_message(
                    chat_id="@chalesh_yarr",
                    text=message,
                    disable_web_page_preview=True
                )
                print("پیام رتبه‌بندی با موفقیت ارسال شد.")
            else:
                print("هیچ اطلاعاتی در رتبه‌بندی موجود نیست.")
                message = "🏆 هنوز هیچ بازیکنی در رتبه‌بندی ثبت نشده است!"
                await client.send_message(
                    chat_id="@chalesh_yarr",
                    text=message,
                    disable_web_page_preview=True
                )
                print("پیام خالی بودن رتبه‌بندی ارسال شد.")
            await asyncio.sleep(10)  # برای تست، 10 ثانیه (برای تولید به 600 تغییر دهید)
        except Exception as e:
            print(f"خطا در announce_leaderboard: {str(e)}")
            await asyncio.sleep(10)  # برای تست، 10 ثانیه


async def cleanup_expired_games():
    while True:
        try:
            print("اجرای تابع cleanup_expired_games...")  # دیباگ
            expired_games = [game_id for game_id, game in games.items() if game.is_expired()]
            for game_id in expired_games:
                print(f"🗑️ بازی {game_id} به دلیل عدم فعالیت حذف شد.")
                del games[game_id]
            await asyncio.sleep(300)
        except Exception as e:
            print(f"خطا در cleanup_expired_games: {str(e)}")
            await asyncio.sleep(300)


def test_db_connection():
    db_path = "plugins/questions.db"
    print(f"بررسی مسیر فایل پایگاه داده: {os.path.abspath(db_path)}")
    if not os.path.exists(db_path):
        print(f"خطا: فایل {db_path} وجود ندارد!")
        return False
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"جدول‌های موجود در پایگاه داده: {tables}")
        table_names = [table[0] for table in tables]
        if "questions_calan" not in table_names:
            print("خطا: جدول questions_calan در پایگاه داده وجود ندارد!")
            conn.close()
            return False
        conn.close()
        return True
    except Exception as e:
        print(f"خطا در تست اتصال به پایگاه داده: {e}")
        return False


def get_random_questions(topic, num_questions):
    db_path = "plugins/questions.db"
    try:
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"فایل پایگاه داده {db_path} پیدا نشد!")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        table_name = f"questions_{topic}"
        cursor.execute(f"SELECT question, option1, option2, correct_answer FROM {table_name}")
        questions = cursor.fetchall()
        conn.close()
        print(f"تعداد سوالات دریافت‌شده از جدول {table_name}: {len(questions)}")

        # فیلتر کردن سوالات استفاده‌نشده
        available_questions = [q for q in questions if str(q) not in used_questions]
        print(f"تعداد سوالات موجود (استفاده‌نشده): {len(available_questions)}")

        if len(available_questions) < num_questions:
            print("هشدار: سوالات موجود کافی نیست، ریست کردن سوالات استفاده‌شده...")
            used_questions.clear()  # ریست کردن سوالات استفاده‌شده
            available_questions = questions

        if len(available_questions) < num_questions:
            raise ValueError(
                f"تعداد سوالات کافی در جدول {table_name} وجود ندارد! نیاز به {num_questions} سوال، اما {len(available_questions)} سوال موجود است.")

        # انتخاب تصادفی سوالات
        selected_questions = random.sample(available_questions, num_questions)

        # اضافه کردن سوالات انتخاب‌شده به لیست استفاده‌شده
        for q in selected_questions:
            used_questions.add(str(q))

        print(f"سوالات انتخاب‌شده: {len(selected_questions)}")
        return selected_questions
    except Exception as e:
        print(f"خطا در دریافت سوالات: {e}")
        return []


# تابع برای ساخت کیبورد گزینه‌ها
def create_options_keyboard(game_id, option1, option2, max_length=20):
    """
    ساخت کیبورد اینلاین برای گزینه‌ها بر اساس طول متن.
    اگر متن گزینه‌ها طولانی باشد، هر گزینه در یک ردیف قرار می‌گیرد.
    max_length: حداکثر طول متنی که در یک ردیف کنار هم قرار می‌گیرد.
    """
    is_long = len(option1) > max_length or len(option2) > max_length
    if is_long:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(f"🔵 {option1}", callback_data=f"{game_id}|option_1")],
            [InlineKeyboardButton(f"🟢 {option2}", callback_data=f"{game_id}|option_2")]
        ])
    else:
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(f"🔵 {option1}", callback_data=f"{game_id}|option_1"),
                InlineKeyboardButton(f"🟢 {option2}", callback_data=f"{game_id}|option_2")
            ]
        ])


print("تست اتصال به پایگاه داده...")
if not test_db_connection():
    print("اسکریپت متوقف شد به دلیل مشکل در اتصال به پایگاه داده.")
    exit(1)

init_leaderboard_db()


@Client.on_inline_query()
async def inline_main_menu(client: Client, inline_query):
    user_id = inline_query.from_user.id
    game = Game(user_id)
    games[game.game_id] = game

    if not await test_channel_access(client):
        await inline_query.answer(
            results=[],
            cache_time=1,
            switch_pm_text="⚠️ ربات به کانال دسترسی ندارد!",
            switch_pm_parameter="error"
        )
        return

    await inline_query.answer(
        results=[
            InlineQueryResultArticle(
                title="🎮 تنظیمات بازی",
                description="تعداد سوال، زمان و دعوت از دوستان",
                input_message_content=InputTextMessageContent(
                    f"به ربات سوالات خوش آمدید!\n{game.get_settings_summary()}\n\n📢 برای شرکت در بازی باید عضو کانال چالش-یار (@chalesh_yarr) باشید."
                ),
                reply_markup=my_start_def_glassButton(game.game_id)
            )
        ],
        cache_time=1
    )


def my_start_def_glassButton(game_id):
    game = games.get(game_id)
    if not game:
        return InlineKeyboardMarkup([[InlineKeyboardButton("❌ بازی منقضی شده", callback_data="expired")]])

    selections = game.selections
    number = selections["number"]
    times = selections["time"]
    topics = selections["topics"]

    def cb(data): return f"{game_id}|{data}"

    return InlineKeyboardMarkup([
        [InlineKeyboardButton("تعداد سوالات", callback_data=cb("numberofQ"))],
        [*[InlineKeyboardButton(f"{n[4:]} ✅" if number == n else n[4:], callback_data=cb(n))
           for n in ["numb6", "numb8", "numb10", "numb12", "numb15", "numb18", "numb20"]]],
        [InlineKeyboardButton("⏱️ زمان پاسخ", callback_data=cb("timeForQ"))],
        [*[InlineKeyboardButton(t[4:] + (" ✅" if t in times else ""), callback_data=cb(t))
           for t in ["time10", "time15", "time20"]]],
        [InlineKeyboardButton("📚 انتخاب موضوع", callback_data=cb("selectTopic"))],
        [
            InlineKeyboardButton("اقتصاد کلان ✅" if "topic_economics" in topics else "اقتصاد کلان",
                                callback_data=cb("topic_economics")),
            InlineKeyboardButton("تاریخ ✅" if "topic_history" in topics else "تاریخ",
                                callback_data=cb("topic_history")),
            InlineKeyboardButton("علمی ✅" if "topic_science" in topics else "علمی", callback_data=cb("topic_science")),
        ],
        [
            InlineKeyboardButton("ادبیات ✅" if "topic_literature" in topics else "ادبیات",
                                callback_data=cb("topic_literature")),
            InlineKeyboardButton("ورزش ✅" if "topic_sports" in topics else "ورزش",
                                callback_data=cb("topic_sports")),
            InlineKeyboardButton("سینما ✅" if "topic_cinema" in topics else "سینما", callback_data=cb("topic_cinema")),
        ],
        [InlineKeyboardButton("🤝 دعوت از دوستان", switch_inline_query=f"start_quiz_{game_id}")],
        [InlineKeyboardButton("🎮 ساخت بازی", callback_data=cb("start_exam"))],
        [InlineKeyboardButton("🗑️ لغو بازی", callback_data=cb("cancel_game"))]
    ])


@Client.on_callback_query()
async def handle_callback_query(client: Client, callback_query: CallbackQuery):
    from_user = callback_query.from_user
    from_user_id = from_user.id
    data = callback_query.data

    if data == "expired":
        await callback_query.answer("❌ این بازی منقضی شده است.", show_alert=True)
        return

    try:
        game_id, pure_data = data.split("|", 1)
        game = games.get(game_id)
        if not game:
            await callback_query.answer("❌ بازی نامعتبر یا منقضی شده است", show_alert=True)
            return
        owner_id = game.owner_id
    except ValueError:
        await callback_query.answer("❌ دکمه نامعتبر", show_alert=True)
        return

    game.update_timestamp()
    selections = game.selections
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

        await callback_query.edit_message_text(
            f"🎯 لطفاً یکی از گزینه‌ها را انتخاب کنید:\n\n{game.get_settings_summary()}\n\n{await get_players_list(client, game_id)}\n\n📢 برای شرکت در بازی باید عضو کانال چالش-یار (@chalesh_yarr) باشید.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ حاضر", callback_data=f"{game_id}|ready_now")],
                [InlineKeyboardButton("🚀 شروع", callback_data=f"{game_id}|start_now")],
                [InlineKeyboardButton("🔙 برگشت به منو", callback_data=f"{game_id}|back_to_menu")],
                [InlineKeyboardButton("🗑️ لغو بازی", callback_data=f"{game_id}|cancel_game")]
            ])
        )
        await callback_query.answer("✅ بازی ساخته شد")
        return
    elif pure_data == "ready_now":
        if not await test_channel_access(client):
            print(f"خطا: ربات به کانال @chalesh_yarr دسترسی ندارد.")
            await callback_query.answer(
                "⚠️ خطای دسترسی ربات! لطفاً ادمین ربات را در کانال @chalesh_yarr بررسی کنید.",
                show_alert=True
            )
            return

        try:
            chat_member = await client.get_chat_member("@chalesh_yarr", from_user_id)
            print(f"وضعیت کاربر {from_user_id} در کانال @chalesh_yarr: {chat_member.status}")

            if chat_member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                if from_user_id not in game.players:
                    game.players.append(from_user_id)
                    user_cache[from_user_id] = from_user
                    print(f"👤 بازیکن جدید: {from_user.first_name} (آیدی: {from_user_id}) به بازی {game_id} اضافه شد.")

                await callback_query.edit_message_text(
                    f"🎯 لطفاً یکی از گزینه‌ها را انتخاب کنید:\n\n{game.get_settings_summary()}\n\n{await get_players_list(client, game_id)}\n\n📢 برای شرکت در بازی باید عضو کانال چالش-یار (@chalesh_yarr) باشید.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("✅ حاضر", callback_data=f"{game_id}|ready_now")],
                        [InlineKeyboardButton("🚀 شروع", callback_data=f"{game_id}|start_now")],
                        [InlineKeyboardButton("🔙 برگشت به منو", callback_data=f"{game_id}|back_to_menu")],
                        [InlineKeyboardButton("🗑️ لغو بازی", callback_data=f"{game_id}|cancel_game")]
                    ])
                )
                await callback_query.answer("✅ شما به لیست بازیکنان اضافه شدید")
            else:
                print(f"وضعیت غیرمجاز برای کاربر {from_user_id}: {chat_member.status}")
                await callback_query.answer("⛔ لطفاً ابتدا عضو کانال چالش-یار (@chalesh_yarr) شوید!", show_alert=True)
        except pyrogram.errors.exceptions.bad_request_400.UserNotParticipant:
            print(f"کاربر {from_user_id} در کانال @chalesh_yarr حضور ندارد.")
            await callback_query.answer("⛔ لطفاً ابتدا عضو کانال چالش-یار (@chalesh_yarr) شوید!", show_alert=True)
        except pyrogram.errors.exceptions.bad_request_400.ChatAdminRequired:
            print(f"خطا: ربات در کانال @chalesh_yarr ادمین نیست یا دسترسی کافی ندارد.")
            await callback_query.answer(
                "⚠️ خطای دسترسی ربات! لطفاً ادمین ربات را در کانال @chalesh_yarr بررسی کنید.",
                show_alert=True
            )
        except Exception as e:
            print(f"خطا در بررسی عضویت کاربر {from_user_id}: {str(e)}")
            await callback_query.answer(
                f"⚠️ خطایی رخ داد: {str(e)}. لطفاً دوباره تلاش کنید یا با ادمین تماس بگیرید.",
                show_alert=True
            )
        return
    elif pure_data == "start_now":
        if from_user_id != owner_id:
            await callback_query.answer("⛔ فقط سازنده می‌تواند بازی را شروع کند", show_alert=True)
            return
        if len(game.players) < 2:
            await callback_query.edit_message_text(
                f"⏳ در انتظار ورود بازیکن (حداقل 2 بازیکن مورد نیاز است):\n\n{game.get_settings_summary()}\n\n{await get_players_list(client, game_id)}\n\n📢 برای شرکت در بازی باید عضو کانال چالش-یار (@chalesh_yarr) باشید.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("✅ حاضر", callback_data=f"{game_id}|ready_now")],
                    [InlineKeyboardButton("🚀 شروع", callback_data=f"{game_id}|start_now")],
                    [InlineKeyboardButton("🔙 برگشت به منو", callback_data=f"{game_id}|back_to_menu")],
                    [InlineKeyboardButton("🗑️ لغو بازی", callback_data=f"{game_id}|cancel_game")]
                ])
            )
            await callback_query.answer("⛔ حداقل 2 بازیکن برای شروع لازم است", show_alert=True)
            return

        time_str = selections["time"][0]
        seconds = int(time_str.replace("time", ""))
        total_questions = game.get_total_questions()

        if "topic_economics" in selections["topics"]:
            game.questions = get_random_questions("calan", total_questions)
        else:
            await callback_query.answer("⚠️ موضوع اقتصاد کلان انتخاب نشده است!", show_alert=True)
            return

        if not game.questions:
            await callback_query.answer("⚠️ خطا در بارگذاری سوالات!", show_alert=True)
            return

        for player_id in game.players:
            game.scores[player_id] = 0

        for question_idx in range(total_questions):
            game.current_question = question_idx + 1
            game.choices[game.current_question] = {}
            question_text, option1, option2, _ = game.questions[question_idx]

            try:
                keyboard = create_options_keyboard(game_id, option1, option2)
                await callback_query.edit_message_text(
                    f"❓ سوال {game.current_question} از {total_questions}\n⏳ {seconds} ثانیه وقت دارید:\n\n{question_text}\n\n{game.get_settings_summary()}",
                    reply_markup=keyboard
                )
            except Exception as e:
                print(f"❌ خطا در نمایش سوال {game.current_question}: {e}")
                break

            await asyncio.sleep(seconds)

        result_lines = ["📊 نتایج بازی:"]

        # مرتب‌سازی بازیکنان بر اساس امتیاز (نزولی)
        sorted_players = sorted(game.players, key=lambda pid: game.scores.get(pid, 0), reverse=True)

        for player_id in sorted_players:
            player_name = user_cache.get(player_id, await client.get_users(player_id)).first_name
            correct_count = game.scores[player_id]
            result_lines.append(f"\n👤 {player_name}: {correct_count} پاسخ درست")
            save_player_score(player_id, player_name, correct_count)
            for question_idx in range(total_questions):
                question_num = question_idx + 1
                choice = game.choices.get(question_num, {}).get(player_id, None)
                if choice:
                    _, _, _, correct_answer = game.questions[question_idx]
                    is_correct = choice[-1] == correct_answer[-1]
                    status = "✅ درست" if is_correct else "❌ اشتباه"
                    symbol = "🔵 گزینه 1" if choice == "option_1" else "🟢 گزینه 2"
                    result_lines.append(f"سوال {question_num}: {symbol} ({status})")
                else:
                    result_lines.append(f"سوال {question_num}: ❓ انتخاب نشده")

        try:
            if callback_query.message:
                await client.send_message(
                    chat_id=callback_query.message.chat.id,
                    text="\n".join(result_lines),
                    disable_web_page_preview=True
                )
            elif callback_query.inline_message_id:
                await callback_query.edit_message_text(
                    text="\n".join(result_lines),
                    disable_web_page_preview=True
                )
            del games[game_id]
        except Exception as e:
            print(f"❌ خطا در ارسال/ویرایش پیام نتایج: {e}")
            await callback_query.answer("⚠️ خطایی در نمایش نتایج رخ داد", show_alert=True)

        return
    elif pure_data in ["option_1", "option_2"]:
        current_question = game.current_question
        if current_question not in game.choices:
            game.choices[current_question] = {}

        if from_user_id in game.choices[current_question]:
            await callback_query.answer("⚠️ شما قبلاً برای این سوال گزینه‌ای انتخاب کرده‌اید", show_alert=True)
            return

        game.choices[current_question][from_user_id] = pure_data
        question_text, _, _, correct_answer = game.questions[current_question - 1]
        is_correct = pure_data[-1] == correct_answer[-1]
        if is_correct:
            game.scores[from_user_id] = game.scores.get(from_user_id, 0) + 1
        await callback_query.answer("✅ پاسخ درست!" if is_correct else "❌ پاسخ نادرست!", show_alert=True)
        return
    elif pure_data == "back_to_menu":
        await callback_query.edit_message_text(
            f"🎮 لطفاً تعداد سوال، زمان و موضوع را انتخاب کنید:\n\n{game.get_settings_summary()}",
            reply_markup=my_start_def_glassButton(game_id)
        )
        await callback_query.answer("🔙 برگشت به منو")
        return
    elif pure_data == "cancel_game":
        if from_user_id != owner_id:
            await callback_query.answer("⛔ فقط سازنده می‌تواند بازی را لغو کند", show_alert=True)
            return
        await callback_query.edit_message_text("🗑️ بازی لغو شد.")
        del games[game_id]
        await callback_query.answer("✅ بازی لغو شد")
        return

    if needs_update:
        try:
            await callback_query.edit_message_text(
                f"🎮 لطفاً تعداد سوال، زمان و موضوع را انتخاب کنید:\n\n{game.get_settings_summary()}",
                reply_markup=my_start_def_glassButton(game_id)
            )
            await callback_query.answer("✅ انتخاب تغییر کرد")
        except pyrogram.errors.exceptions.bad_request_400.MessageNotModified:
            pass
    else:
        await callback_query.answer("⚠️ این گزینه از قبل انتخاب شده")


async def get_players_list(client, game_id):
    game = games.get(game_id, Game(0))
    if not game.players:
        return "⏳ هنوز بازیکنی اضافه نشده!"

    players_list = []
    for user_id in game.players:
        if user_id not in user_cache:
            user_cache[user_id] = await client.get_users(user_id)
        players_list.append(f"👤 {user_cache[user_id].first_name}")

    return "👥 بازیکنان حاضر:\n" + "\n".join(players_list)


print("پلاگین startbot با موفقیت لود شد.")  # دیباگ: تأیید لود کامل