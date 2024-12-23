from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from Grabber import user_collection
from . import capsify, app
from .block import block_dec, temp_block

MAX_SALES_SLOT = 5
MIN_SALE_PRICE = 10000
MAX_SALE_PRICE = 500000

@app.on_message(filters.command("sale"))
@block_dec
async def sale_command(client, message):
    user_id = message.from_user.id
    if temp_block(user_id):
        return
    if len(message.command) != 3:
        await message.reply(capsify("USAGE: /SALE (CHARACTER_ID) (AMOUNT)"))
        return

    character_id = message.command[1]
    try:
        sale_price = int(message.command[2])
    except ValueError:
        await message.reply(capsify("THE SALE PRICE MUST BE A NUMBER❗"))
        return

    if not (MIN_SALE_PRICE <= sale_price <= MAX_SALE_PRICE):
        await message.reply(
            capsify(f"THE SALE PRICE MUST BE BETWEEN {MIN_SALE_PRICE} AND {MAX_SALE_PRICE} GOLD❗")
        )
        return

    user = await user_collection.find_one({'id': user_id})
    if not user:
        await message.reply(capsify("YOU HAVE NO CHARACTERS IN YOUR COLLECTION❗"))
        return

    character = next(
        (char for char in user.get('characters', []) if char['id'] == character_id), None
    )
    if not character:
        await message.reply(capsify(f"CHARACTER WITH ID {character_id} NOT FOUND IN YOUR COLLECTION❗"))
        return

    sales_slot = user.get('sales_slot', [])
    if len(sales_slot) >= MAX_SALES_SLOT:
        await message.reply(capsify("YOUR SALES SLOT IS FULL❗ REMOVE A CHARACTER TO ADD A NEW ONE."))
        return

    # Add sale details
    character['sprice'] = sale_price
    sales_slot.append(character)

    await user_collection.update_one(
        {'id': user_id}, {'$set': {'sales_slot': sales_slot}}
    )

    await message.reply(
        capsify(
            f"ADDED TO SALE ✅\n\n"
            f"NAME: {capsify(character['name'])}\n"
            f"ANIME: {capsify(character['anime'])}\n"
            f"RARITY: {capsify(character.get('rarity', 'UNKNOWN'))}\n"
            f"ID: {character_id}\n"
            f"SALE PRICE: {sale_price} GOLD"
        ),
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(capsify("CLOSE"), callback_data=f"SALE_SLOT_CLOSE_{user_id}")]]
        )
    )


@app.on_message(filters.command("mysales"))
@block_dec
async def my_sales_command(client, message):
    user_id = message.from_user.id
    if temp_block(user_id):
        return
    user = await user_collection.find_one({'id': user_id})
    if not user or not user.get('sales_slot'):
        await message.reply(capsify("YOU HAVE NO CHARACTERS IN YOUR SALES SLOT❗"))
        return

    sales = user['sales_slot']
    sales_list = f"{capsify(message.from_user.first_name)}'S SALES\n\n"
    for idx, sale in enumerate(sales, 1):
        sales_list += (capsify(
            f"{idx}. {capsify(sale['name'])}\n"
            f"ANIME: {capsify(sale['anime'])}\n"
            f"RARITY: {capsify(sale.get('rarity', 'UNKNOWN'))}\n"
            f"ORIGINAL PRICE: {sale.get('price', 'UNKNOWN')} GOLD\n"
            f"SALE PRICE: {sale['sprice']} GOLD\n"
            f"ID: {sale['id']}\n\n"
        ))

    await message.reply(
        sales_list,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(capsify("CLOSE"), callback_data=f"SALE_SLOT_CLOSE_{user_id}")]]
        )
    )


@app.on_message(filters.command("sales"))
async def sales_command(client, message):
    if message.reply_to_message:
        target_user_id = message.reply_to_message.from_user.id
    elif len(message.command) == 2:
        try:
            target_user_id = int(message.command[1])
        except ValueError:
            await message.reply(capsify("INVALID USER ID PROVIDED❗"))
            return
    else:
        await message.reply(capsify("USAGE: /SALES (USER_ID) OR AS A REPLY TO A USER❗"))
        return

    if target_user_id == message.from_user.id:
        await message.reply(capsify("USE /MYSALES TO VIEW YOUR OWN SALES❗"))
        return

    user = await user_collection.find_one({'id': target_user_id})
    if not user or not user.get('sales_slot'):
        await message.reply(capsify("THE USER HAS NO CHARACTERS IN THEIR SALES SLOT❗"))
        return

    sales = user['sales_slot']
    sales_list = f"{capsify('SALES FOR')} {capsify(user.get('first_name', 'UNKNOWN'))}\n\n"
    buttons = []

    for idx, sale in enumerate(sales, 1):
        sales_list += (capsify(
            f"{idx}. {capsify(sale['name'])}\n"
            f"ANIME: {capsify(sale['anime'])}\n"
            f"RARITY: {capsify(sale.get('rarity', 'UNKNOWN'))}\n"
            f"SALE PRICE: {sale['sprice']} GOLD\n"
            f"ID: {sale['id']}\n\n"
        ))
        buttons.append(
            InlineKeyboardButton(str(idx), callback_data=f"VIEW_SALE_{idx}_{target_user_id}_{message.from_user.id}")
        )

    await message.reply(
        sales_list,
        reply_markup=InlineKeyboardMarkup(
            [
                buttons,
                [InlineKeyboardButton(capsify("CLOSE"), callback_data=f"SALE_SLOT_CLOSE_{message.from_user.id}")],
            ]
        )
    )


@app.on_callback_query(filters.regex(r"VIEW_SALE_(\d+)_(\d+)_(\d+)"))
async def view_sale_details(client, callback_query):
    slot_index = int(callback_query.matches[0].group(1)) - 1
    target_user_id = int(callback_query.matches[0].group(2))
    buyer_id = int(callback_query.matches[0].group(3))

    if callback_query.from_user.id != buyer_id:
        await callback_query.answer(capsify("THIS IS NOT FOR YOU, BAKA❗"), show_alert=True)
        return

    user = await user_collection.find_one({'id': target_user_id})
    if not user or not user.get('sales_slot') or slot_index >= len(user['sales_slot']):
        await callback_query.answer(capsify("THIS SALES SLOT DOES NOT EXIST❗"), show_alert=True)
        return

    sale = user['sales_slot'][slot_index]
    sale_details = (capsify(
        f"NAME: {capsify(sale['name'])}\n"
        f"ANIME: {capsify(sale['anime'])}\n"
        f"RARITY: {capsify(sale.get('rarity', 'UNKNOWN'))}\n"
        f"PRICE: {sale['sprice']} GOLD\n"
        f"ID: {sale['id']}\n"
    ))

    buttons = []
    if callback_query.from_user.id == buyer_id:
        buttons.append([InlineKeyboardButton(capsify("PURCHASE"), callback_data=f"SALE_PURCHASE_{sale['id']}_{target_user_id}_{buyer_id}")])

    buttons.append([InlineKeyboardButton(capsify("CLOSE"), callback_data=f"SALE_SLOT_CLOSE_{message.from_user_id}")])

    await callback_query.message.edit_text(sale_details, reply_markup=InlineKeyboardMarkup(buttons))


@app.on_callback_query(filters.regex(r"SALE_PURCHASE_(\d+)_(\d+)_(\d+)"))
async def purchase_character(client, callback_query):
    buyer_id = callback_query.from_user.id
    sale_id = int(callback_query.matches[0].group(1))
    seller_id = int(callback_query.matches[0].group(2))

    if buyer_id == seller_id:
        await callback_query.answer(capsify("YOU CANNOT PURCHASE YOUR OWN CHARACTER❗"), show_alert=True)
        return

    buyer = await user_collection.find_one({'id': buyer_id})
    seller = await user_collection.find_one({'id': seller_id})

    if not buyer or not seller or not seller.get('sales_slot'):
        await callback_query.answer(capsify("SALE NOT FOUND❗"), show_alert=True)
        return

    sale = next((s for s in seller['sales_slot'] if s['id'] == str(sale_id)), None)
    if not sale:
        await callback_query.answer(capsify("CHARACTER NO LONGER AVAILABLE FOR SALE❗"), show_alert=True)
        return

    buyer_gold = buyer.get('gold', 0)
    if buyer_gold < sale['sprice']:
        await callback_query.answer(capsify("YOU DO NOT HAVE ENOUGH GOLD TO PURCHASE THIS CHARACTER❗"), show_alert=True)
        return

    buyer_gold -= sale['sprice']
    seller['sales_slot'].remove(sale)
    await user_collection.update_one({'id': seller_id}, {'$set': {'sales_slot': seller['sales_slot']}})
    await user_collection.update_one({'id': buyer_id}, {'$set': {'gold': buyer_gold}})
    await user_collection.update_one(
        {'id': buyer_id}, {'$push': {'characters': {key: sale[key] for key in sale if key not in ['sprice']}}}
    )

    await callback_query.message.edit_text(
        capsify(f"PURCHASE SUCCESSFUL❗ {sale['name']} HAS BEEN ADDED TO YOUR COLLECTION❗")
    )


@app.on_callback_query(filters.regex(r"SALE_SLOT_CLOSE_(\d+)"))
async def sale_slot_close(client, callback_query):
    target_user_id = int(callback_query.matches[0].group(1))
    if callback_query.from_user.id != target_user_id:
        await callback_query.answer(capsify("THIS IS NOT FOR YOU, BAKA❗"), show_alert=True)
        return
    await callback_query.message.delete()


@app.on_message(filters.command("rmsales"))
async def remove_sales_command(client, message):
    user_id = message.from_user.id
    if len(message.command) != 2:
        await message.reply(capsify("USAGE: /RMSALES (CHARACTER_ID)"))
        return

    character_id = message.command[1]
    user = await user_collection.find_one({'id': user_id})
    if not user or not user.get('sales_slot'):
        await message.reply(capsify("YOU HAVE NO CHARACTERS IN YOUR SALES SLOT❗"))
        return

    sales_slot = user['sales_slot']
    sale = next((s for s in sales_slot if s['id'] == character_id), None)
    if not sale:
        await message.reply(capsify("CHARACTER NOT FOUND IN YOUR SALES SLOT❗"))
        return

    sales_slot.remove(sale)
    await user_collection.update_one({'id': user_id}, {'$set': {'sales_slot': sales_slot}})
    await message.reply(capsify("CHARACTER REMOVED FROM SALES SLOT❗"))