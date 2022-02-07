import json
import os

from aiogram import types
from dispatcher import dp
from classes import GetDataFromUser

config = open(os.getcwd() + "/config.json", encoding="UTF-8")
data = json.loads(config.read())
config.close()

@dp.message_handler(commands=['profile'])
async def profile_handler(message: types.Message):
    try:
        value = GetDataFromUser.is_user_data(message.from_user.id)
        if message.chat.id == message.from_user.id and not value:
            GetDataFromUser.create_user_data(message.from_user.id)

        if message.chat.id != message.from_user.id and not value:
            return

        data_user = GetDataFromUser.get_data_user(message.from_user.id)

        profile = f'{data["emojio"]} {message.from_user.full_name}, ваш профиль:\n\n'
        profile += f'📌 Ваш ID: *{data_user["player_uid"]}*\n'
        profile += f'💰 Баланс: *{data_user["player_balance"]} $*'
        if data_user["player_referal_balance"] != 0:
            profile += f'\n💸 Реф.Баланс: *{data_user["player_referal_balance"]} $*'

        return await message.reply(text=profile)
    except Exception as e:
        print(repr(e))
