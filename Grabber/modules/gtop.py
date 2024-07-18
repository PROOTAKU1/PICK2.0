from pyrogram import Client, filters
from . import user_collection, app
import asyncio

@app.on_message(filters.command("gtop"))
async def gtop_command(client, message):
    top_users = await user_collection.find().sort('gold', -1).limit(10).to_list(10)

    if not top_users:
        await message.reply_text("No users found.")
        return

    response_message = "Top Collectors:\n\n"
    for index, user in enumerate(top_users, start=1):
        first_name = user.get('first_name', 'None')
        response_message += f"**{index}. {first_name}** - {user['gold']} gold\n"

    await message.reply_text(response_message)