
from pyrogram import Client

Plugins = dict(root="plugins")

app = Client(name = "eghtesad",
            #  api_id = 21612565,
             plugins=Plugins,
            #  api_hash = "d5c851ae1170ac168f6ac04ad085da12",
             bot_token="8124230199:AAG87vZW4VZSW7QGJBJH1vYmKP5isXLj8hs"
             )


    
app.run()