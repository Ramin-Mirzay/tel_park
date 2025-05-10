
import os
import asyncio
from pyrogram import Client
from plugins.startbot import start_background_tasks  # وارد کردن تابع از پلاگین

Plugins = dict(root="plugins")

class CustomClient(Client):
    async def start(self):
        await super().start()  # اجرای متد start اصلی
        print("ربات آماده شد! فراخوانی start_background_tasks...")  # دیباگ
        try:
            await start_background_tasks(self)  # فراخوانی تسک‌های پس‌زمینه
        except Exception as e:
            print(f"خطا در فراخوانی start_background_tasks: {str(e)}")

app = CustomClient(
    name="eghtesad",
    plugins=Plugins,
    bot_token=os.getenv("BOT_TOKEN", "8124230199:AAG87vZW4VZSW7QGJBJH1vYmKP5isXLj8hs")
)

app.run()

# import os
# import asyncio
# from pyrogram import Client
# from plugins.startbot import start_background_tasks  # وارد کردن تابع از پلاگین
#
# Plugins = dict(root="plugins")
#
# class CustomClient(Client):
#     async def start(self):
#         await super().start()  # اجرای متد start اصلی
#         print("ربات آماده شد! فراخوانی start_background_tasks...")  # دیباگ
#         try:
#             await start_background_tasks(self)  # فراخوانی تسک‌های پس‌زمینه
#         except Exception as e:
#             print(f"خطا در فراخوانی start_background_tasks: {str(e)}")
#
# app = CustomClient(
#     name="eghtesad",
#     plugins=Plugins,
#     bot_token=os.getenv("BOT_TOKEN", "8124230199:AAG87vZW4VZSW7QGJBJH1vYmKP5isXLj8hs")
# )
#
# app.run()
# import os
# import asyncio
# from pyrogram import Client
# from plugins.startbot import start_background_tasks  # وارد کردن تابع از پلاگین
#
# Plugins = dict(root="plugins")
#
# class CustomClient(Client):
#     async def start(self):
#         await super().start()  # اجرای متد start اصلی
#         print("ربات آماده شد! فراخوانی start_background_tasks...")  # دیباگ
#         try:
#             await start_background_tasks(self)  # فراخوانی تسک‌های پس‌زمینه
#         except Exception as e:
#             print(f"خطا در فراخوانی start_background_tasks: {str(e)}")
#
# app = CustomClient(
#     name="eghtesad",
#     plugins=Plugins,
#     bot_token=os.getenv("BOT_TOKEN", "8124230199:AAG87vZW4VZSW7QGJBJH1vYmKP5isXLj8hs")
# )
#
# app.run()


#
# import os
# from pyrogram import Client
#
# Plugins = dict(root="plugins")
#
# app = Client(
#     name="eghtesad",
#     plugins=Plugins,
#     bot_token=os.getenv("BOT_TOKEN", "8124230199:AAG87vZW4VZSW7QGJBJH1vYmKP5isXLj8hs")
# )
#
# app.run()



# from pyrogram import Client
#
# Plugins = dict(root="plugins")
#
# app = Client(name = "eghtesad",
#
#              plugins=Plugins,
#
#              bot_token="8124230199:AAG87vZW4VZSW7QGJBJH1vYmKP5isXLj8hs"
#              )
#
#
#
# app.run()