import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
import random
from datetime import datetime, timedelta
from Grabber import collection, user_collection, user_totals_collection
from . import add as add_balance, deduct as deduct_balance, app

rarity_map = {
    "🟢 Common": True,
    "🔵 Medium": True,
    "🟠 Rare": True,
    "🟡 Legendary": True,
    "🪽 Celestial": True,
}

last_propose_times = {}
proposing_users = {}

@app.on_message(filters.command("propose") )
async def propose(client, message: Message):
    user_id = message.from_user.id

    user_data = await user_collection.find_one({'id': user_id})

    if not user_data or int(user_data.get('balance', 0)) < 20000:
        await message.reply_text("You need at least 20000 tokens to propose.")
        proposing_users[user_id] = False
        return

    if proposing_users.get(user_id):
        await message.reply_text("You are already proposing. Please wait for the current proposal to finish.")
        proposing_users[user_id] = False
        return
    else:
        proposing_users[user_id] = True

    last_propose_time = last_propose_times.get(user_id)
    if last_propose_time:
        time_since_last_propose = datetime.now() - last_propose_time
        if time_since_last_propose < timedelta(minutes=5):
            remaining_cooldown = timedelta(minutes=5) - time_since_last_propose
            remaining_cooldown_minutes = remaining_cooldown.total_seconds() // 60
            remaining_cooldown_seconds = remaining_cooldown.total_seconds() % 60
            await message.reply_text(f"Cooldown! Please wait {int(remaining_cooldown_minutes)}m {int(remaining_cooldown_seconds)}s before proposing again.")
            proposing_users[user_id] = False
            return

    await deduct_balance(user_id, 10000)

    proposal_message = "✨ 𝐓𝐢𝐦𝐞 𝐭𝐨 𝐏𝐫𝐨𝐩𝐨𝐬𝐞 ✨"
    photo_path = 'https://telegra.ph/file/68491359070e2e045c919.jpg'
    await message.reply_photo(photo=photo_path, caption=proposal_message)

    await asyncio.sleep(2)

    await message.reply_text("𝐀𝐬𝐤𝐢𝐧𝐠 𝐟𝐨𝐫 𝐇𝐞𝐫 𝐇𝐚𝐧𝐝 💍")

    await asyncio.sleep(2)

    if random.random() < 0.6:
        rejection_message = "𝐒𝐡𝐞 𝐩𝐮𝐬𝐡𝐞𝐝 𝐲𝐨𝐮 𝐚𝐰𝐚𝐲 𝐚𝐧𝐝 𝐬𝐜𝐫𝐞𝐚𝐦𝐞𝐝 😂"
        rejection_photo_path = 'https://graph.org/file/43ac16b34453bafe480d9.jpg'
        await message.reply_photo(photo=rejection_photo_path, caption=rejection_message)
    else:
        all_characters = list(await collection.find({}).to_list(length=None))
        valid_characters = [char for char in all_characters if char.get('rarity') in rarity_map.keys()]

        if not valid_characters:
            await message.reply_text("No characters available with the specified rarity.")
            return

        character = random.choice(valid_characters)
        await user_collection.update_one({'id': user_id}, {'$push': {'characters': character}})
        await message.reply_photo(photo=character['img_url'], caption=f"{character['name']} accepted your proposal!")

    last_propose_times[user_id] = datetime.now()
    proposing_users[user_id] = False