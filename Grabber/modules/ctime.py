from pymongo import ReturnDocument
from pyrogram import Client, filters
from pyrogram.types import Message
from . import sudo_filter, application, user_totals_collection, app

@app.on_message(filters.command("changetime") & ~filters.edited & filters.group & filters.admins)
async def change_time(client: Client, message: Message):
    try:
        user = await client.get_chat_member(message.chat.id, message.from_user.id)
        if user.status not in ('administrator', 'creator'):
            await message.reply_text('You do not have permission to use this command.')
            return

        args = message.command[1:]
        if len(args) != 1:
            await message.reply_text('Incorrect format. Please use: /changetime NUMBER')
            return

        new_frequency = int(args[0])
        if new_frequency < 100:
            await message.reply_text('The message frequency must be greater than or equal to 100.')
            return

        if new_frequency > 10000:
            await message.reply_text('That\'s too much frequency. Use below 10000')
            return

        chat_frequency = await user_totals_collection.find_one_and_update(
            {'chat_id': str(message.chat.id)},
            {'$set': {'message_frequency': new_frequency}},
            upsert=True,
            return_document=ReturnDocument.AFTER
        )

        await message.reply_text(f'Successfully changed character appearance frequency to every {new_frequency} messages.')

    except Exception as e:
        await message.reply_text('Failed to change character appearance frequency.')

# Define change_time_sudo function with sudo filter
@app.on_message(filters.command("ctime") & ~filters.edited)
@sudo_filter
async def change_time_sudo(client: Client, message: Message):
    try:
        args = message.command[1:]
        if len(args) != 1:
            await message.reply_text('Incorrect format. Please use: /ctime NUMBER')
            return

        new_frequency = int(args[0])
        if new_frequency < 1:
            await message.reply_text('The message frequency must be greater than or equal to 1')
            return

        if new_frequency > 10000:
            await message.reply_text('That\'s too much frequency. Use below 10000')
            return

        chat_frequency = await user_totals_collection.find_one_and_update(
            {'chat_id': str(message.chat.id)},
            {'$set': {'message_frequency': new_frequency}},
            upsert=True,
            return_document=ReturnDocument.AFTER
        )

        await message.reply_text(f'Successfully changed character appearance frequency to every {new_frequency} messages.')

    except Exception as e:
        await message.reply_text('Failed to change character appearance frequency.')
