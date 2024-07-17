from pyrogram import Client, filters
from pyrogram.types import Message
from datetime import datetime, timedelta
import math
from . import add, deduct, show, abank, dbank, sbank, user_collection, Grabberu

last_payment_times = {}
last_loan_times = {}

async def handle_error(client: Client, message: Message, error: Exception):
    await message.reply_text(f"An error occurred: {str(error)}")
    print(f"Error: {error}")

async def save(client: Client, message: Message):
    try:
        amount = int(message.command[1])
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")
    except (IndexError, ValueError) as e:
        await handle_error(client, message, e)
        return

    user_id = message.from_user.id
    user_data = await user_collection.find_one({'id': user_id}, projection={'balance': 1})

    if user_data:
        balance_amount = int(user_data.get('balance', 0))

        if amount > balance_amount:
            await message.reply_text("Insufficient balance to save this amount.")
            return

        await deduct(user_id, amount)
        await abank(user_id, amount)

        await message.reply_text(f"You saved Ŧ{amount} in your bank account.")
    else:
        await message.reply_text("User data not found.")

async def withdraw(client: Client, message: Message):
    try:
        amount = int(message.command[1])
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")
    except (IndexError, ValueError) as e:
        await handle_error(client, message, e)
        return

    user_id = message.from_user.id
    user_data = await user_collection.find_one({'id': user_id}, projection={'balance': 1, 'saved_amount': 1})

    if user_data:
        saved_amount = int(user_data.get('saved_amount', 0))

        if amount > saved_amount:
            await message.reply_text("Insufficient saved amount to withdraw.")
            return

        await add(user_id, amount)
        await dbank(user_id, amount)

        await message.reply_text(f"You withdrew Ŧ{amount} from your bank account.")
    else:
        await message.reply_text("User data not found.")

async def loan(client: Client, message: Message):
    try:
        loan_amount = int(message.command[1])
        if loan_amount <= 0 or loan_amount > 10000000000000:
            raise ValueError("Amount must be between 1 and 10000000000000.")
    except (IndexError, ValueError) as e:
        await handle_error(client, message, e)
        return

    user_id = message.from_user.id
    user_data = await user_collection.find_one({'id': user_id}, projection={'balance': 1, 'loan_amount': 1})

    if user_data:
        if 'loan_amount' in user_data and user_data['loan_amount'] > 0:
            await message.reply_text("You still have an existing loan. Please repay it before taking a new one.")
            return

        current_time = datetime.now()
        loan_due_date = current_time + timedelta(days=10)

        new_balance = int(user_data.get('balance', 0)) + loan_amount
        await user_collection.update_one(
            {'id': user_id},
            {'$set': {'loan_amount': loan_amount, 'loan_due_date': loan_due_date}}
        )
        await add(user_id, loan_amount)

        await message.reply_text(f"You successfully took a loan of Ŧ{loan_amount}. You must repay it within 10 days to avoid a penalty.")
        log_message = f"Loan: +{loan_amount} tokens | User ID: {user_id} | Time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}"
        await client.send_message(926282726, log_message)  
    else:
        await message.reply_text("User data not found.")

async def repay(client: Client, message: Message):
    try:
        repayment_amount = int(message.command[1])
        if repayment_amount <= 0:
            raise ValueError("Amount must be greater than zero.")
    except (IndexError, ValueError) as e:
        await handle_error(client, message, e)
        return

    user_id = message.from_user.id
    user_data = await user_collection.find_one({'id': user_id}, projection={'balance': 1, 'loan_amount': 1, 'loan_due_date': 1})

    if user_data:
        loan_amount = user_data.get('loan_amount', 0)
        loan_due_date = user_data.get('loan_due_date')
        current_time = datetime.now()

        if repayment_amount > loan_amount:
            await message.reply_text("Repayment amount cannot exceed the loan amount.")
            return

        if current_time > loan_due_date:
            overdue_hours = (current_time - loan_due_date).total_seconds() / 3600
            penalty = math.ceil(overdue_hours) * (loan_amount * 0.05)
            repayment_amount += penalty
            await message.reply_text(f"You have a penalty of Ŧ{penalty:.2f} due to late repayment.")

        new_loan_amount = loan_amount - repayment_amount

        await user_collection.update_one({'id': user_id}, {'$set': {'loan_amount': new_loan_amount}})
        await deduct(user_id, repayment_amount)

        await message.reply_text(f"You successfully repaid Ŧ{repayment_amount} of your loan.")
    else:
        await message.reply_text("User data not found.")

@Grabberu.on_message(filters.command("loan"))
async def loan_handler(client: Client, message: Message):
    await loan(client, message)

@Grabberu.on_message(filters.command("save"))
async def save_handler(client: Client, message: Message):
    await save(client, message)

@Grabberu.on_message(filters.command("repay"))
async def repay_handler(client: Client, message: Message):
    await repay(client, message)

@Grabberu.on_message(filters.command("withdraw"))
async def withdraw_handler(client: Client, message: Message):
    await withdraw(client, message)
