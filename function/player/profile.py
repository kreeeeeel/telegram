import json
import os
import logging

from aiogram import types
from dispatcher import dp
from classes import GetDataFromUser, GetDataFromChat

config = open(os.getcwd() + "/config.json", encoding="UTF-8")
data = json.loads(config.read())
config.close()

@dp.message_handler(commands=['profile'])
async def profile_handler(message: types.Message):
    try:
        if message.chat.id != message.from_user.id:
            chat = GetDataFromChat.export_data_from_chat(chat=message.chat.id)
            if chat["working"] is False:
                return

        value = GetDataFromUser.is_user_data(message.from_user.id)
        if message.chat.id == message.from_user.id and not value:
            GetDataFromUser.create_user_data(message.from_user.id)

        if message.chat.id != message.from_user.id and not value:
            return

        data_user = GetDataFromUser.get_data_user(message.from_user.id)

        profile = f'{data["emojio"]} {message.from_user.full_name}, ваш профиль:\n\n'
        profile += f'📌 Ваш ID: *{data_user["player_uid"]}*\n'
        profile += f'💰 Баланс: *{data_user["player_balance"]:,d} $*'
        if data_user["player_referal_balance"] != 0:
            profile += f'\n💸 Реф.Баланс: *{data_user["player_referal_balance"]:,d} $*'

        return await message.reply(text=profile)
    except Exception as e:
        logging.error(e, exc_info=True)
