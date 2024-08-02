import requests
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ChatAction
from . import app

@app.on_message(filters.command("cosplay"))
async def cosplay(_, msg):
    bot_info = await app.get_me()
    bot_username = bot_info.username

    DRAGONS = [
        [
            InlineKeyboardButton(text="ᴀᴅᴅ ᴍᴇ ʙᴀʙʏ", url=f"https://t.me/{bot_username}?startgroup=true"),
        ],
    ]

    img = requests.get("https://waifu-api.vercel.app").json()
    await msg.reply_photo(img, caption=f"❅ ᴄᴏsᴘʟᴀʏ ʙʏ ➠ ๛ᴅ ʀ ᴀ ɢ ᴏ ɴ s ༗", reply_markup=InlineKeyboardMarkup(DRAGONS))
