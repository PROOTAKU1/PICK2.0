import requests
from pyrogram import Client, filters
from pyrogram.types import Message
from pymongo import ReturnDocument
import random
from . import uploader_filter, app
from Grabber import collection, db, CHARA_CHANNEL_ID

# Function to get the next sequence ID from MongoDB
async def get_next_sequence_number(sequence_name):
    sequence_collection = db.sequences
    sequence_document = await sequence_collection.find_one_and_update(
        {'_id': sequence_name},
        {'$inc': {'sequence_value': 1}},
        return_document=ReturnDocument.AFTER
    )
    if not sequence_document:
        await sequence_collection.insert_one({'_id': sequence_name, 'sequence_value': 0})
        return 0
    return sequence_document['sequence_value']

# New Rarity System (1-20)
rarity_map = {
    1: "⚪ COMMON",
    2: "🟢 MEDIUM",
    3: "🟣 RARE",
    4: "🟡 LEGENDARY",
    5: "🏖️ HOT",
    6: "❄ COLD",
    7: "💞 LOVE",
    8: "🎃 SCARY",
    9: "🎄 CHRISTMAS",
    10: "✨ SPECIAL EDITION",
    11: "💫 SHINING",
    12: "🪽 ANGELIC",
    13: "🧬 MIX WORLD",
    14: "🔮 DELUXE EDITION",
    15: "🥵 MYSTIC",
    16: "👑 ROYAL",
    17: "👗 COSPLAY",
    18: "🌍 UNIVERSAL",
    19: "🎁 GIVEAWAY",
    20: "🎨 CUSTOM"
}

# Upload image to Catbox
def upload_to_catbox(photo_path):
    url = "https://catbox.moe/user/api.php"
    with open(photo_path, 'rb') as photo:
        response = requests.post(
            url,
            data={'reqtype': 'fileupload'},
            files={'fileToUpload': photo}
        )
    if response.status_code == 200 and response.text.startswith("https://"):
        return response.text.strip()
    else:
        raise Exception(f"Catbox upload failed: {response.text}")

# Uploader Command
@app.on_message(filters.command('upload') & uploader_filter)
async def upload(client: Client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.photo:
        await message.reply_text("❌ **Please reply to an image with the caption:**\n\n"
                                 "𝙽𝙰𝙼𝙴: Character Name\n"
                                 "ᴀɴɪᴍᴇ: Anime Name\n"
                                 "𝚁𝙰𝚁𝙸𝚃𝚈: Number (1-20)")
        return

    caption_lines = message.reply_to_message.caption.strip().split("\n")

    if len(caption_lines) < 3:
        await message.reply_text("⚠ **Incorrect format. Use:**\n"
                                 "𝙽𝙰𝙼𝙴: Character Name\n"
                                 "ᴀɴɪᴍᴇ: Anime Name\n"
                                 "𝚁𝙰𝚁𝙸𝚃𝚈: Number (1-20)")
        return

    try:
        character_name = caption_lines[0].split(": ", 1)[1].strip().title()
        anime = caption_lines[1].split(": ", 1)[1].strip().title()
        rarity_number = int(caption_lines[2].split(": ", 1)[1].strip())

        if rarity_number not in rarity_map:
            raise ValueError("Invalid rarity number")

        rarity = rarity_map[rarity_number]

    except (IndexError, ValueError, KeyError):
        await message.reply_text("⚠ **Invalid format or rarity number. Please use a number between 1-20.**")
        return

    try:
        # Download Image
        photo = await client.download_media(message.reply_to_message.photo)
        img_url = upload_to_catbox(photo)

        # Generate Unique ID & Random Price
        id = str(await get_next_sequence_number('character_id')).zfill(2)
        price = random.randint(60000, 80000)

        # Send Character to Channel
        sent_message = await client.send_photo(
            chat_id=CHARA_CHANNEL_ID,
            photo=img_url,
            caption=(
                "𝐂𝐡𝐚𝐫𝐚𝐜𝐭𝐞𝐫 𝐃𝐞𝐭𝐚𝐢𝐥𝐬 ‼️\n\n"
                f"𝙽𝙰𝙼𝙴: {character_name}\n"
                f"ᴀɴɪᴍᴇ: {anime}\n"
                f"𝚁𝙰𝚁𝙸𝚃𝚈: {rarity}\n\n"
                f"💰 𝗣𝗿𝗶𝗰𝗲: {price}\n"
                f"🆔 𝗜𝗗: {id}\n"
                f"👤 𝗔𝗱𝗱𝗲𝗱 𝗕𝘆: {message.from_user.first_name}"
            )
        )

        # Save Character Data in MongoDB
        character = {
            'img_url': img_url,
            'name': character_name,
            'anime': anime,
            'rarity': rarity,
            'price': price,
            'id': id,
            'message_id': sent_message.id
        }

        await collection.insert_one(character)
        await message.reply_text("✅ **Character Uploaded Successfully!**")

    except Exception as e:
        await message.reply_text(f"❌ **Error:** {str(e)}")
