from aiogram import types
from dispatcher import dp

from . import mafia
from . import admin
from . import blackjack
from . import double

from dispatcher import dp, bot
from classes import GetDataFromChat

@dp.message_handler(commands=['startgame'])
async def start_handler(message: types.Message):
    try:
        if message.from_user.id != message.chat.id:

            if not await admin.is_admin_group(chat_id=message.chat.id, user_id=message.from_user.id):
                return

            if not GetDataFromChat.is_created_chat(message.chat.id):
                return 

            if await admin.is_admin_group(message.chat.id, bot.id):
                await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

            chat = GetDataFromChat.export_data_from_chat(chat=message.chat.id)
            if chat["action"] == "Mafia" and chat["type"] == "Register":
                return await mafia.countdown_mafia(chat_id=message.chat.id, forcibly=True)

            if chat["action"] == "Black-Jack" and chat["type"] == "Register":
                return await blackjack.countdown_blackjack(chat_id=message.chat.id, forcibly=True)

            if chat["action"] == "Double":
                return await double.countdown_double(chat_id=message.chat.id, forcibly=True)

    except Exception as e:
        print("Не удалось обработать команду: ", e)