import json
import os
import logging

from aiogram import types
from dispatcher import dp, bot

from classes import GetDataFromUser, GetDataFromChat

config = open(os.getcwd() + "/config.json", encoding="UTF-8")
data = json.loads(config.read())
config.close()

@dp.message_handler(commands=['transfer'])
async def transfer_handler(message: types.Message):
    try:
        if message.chat.id != message.from_user.id:
            chat = GetDataFromChat.export_data_from_chat(chat=message.chat.id)
            if chat["working"] is False:
                return

        if not GetDataFromUser.is_user_data(user_id=message.from_user.id):
            return 

        arg = message.get_args()

        split = arg.split(" ")
        if len(split) != 2 or not split[1].isdigit() or not split[0].isdigit():
            return await message.reply(data["emojio"] + " Используйте: /transfer <ID пользователя> <Сумму>")

        transfer_id = int(split[0])
        transfer_money = int(split[1])

        data_user = GetDataFromUser.get_data_user(user_id=message.from_user.id)

        if data["minimal_transfer_money"] > transfer_money:
            return await message.reply(data["emojio"] + ' Минимальная сумма перевода *{data["minimal_transfer_money"]} $*')

        if data_user["player_uid"] == transfer_id:
            return await message.reply(data["emojio"] + " Хех.. самому себе передавать нельзя.")

        if data_user["player_balance"] < transfer_money:
            return await message.reply(data["emojio"] + " У вас недостаточно средств..")

        dirs = os.listdir(os.getcwd() + "/data/users")

        transfer_telegram_id = None
        for temp in dirs:

            with open(os.getcwd() + "/data/users/" + temp, encoding="UTF-8") as file:
                user = json.loads(file.read())

            if user["player_uid"] == transfer_id:
                transfer_telegram_id = int(temp.replace(".json", ""))
                break

        if not transfer_telegram_id:
            return await message.reply(data["emojio"] + " Пользователь с данным *ID* не найден")

        data_user["player_balance"] -= transfer_money
        user["player_balance"] += transfer_money
        GetDataFromUser.set_data_user(user_id=transfer_telegram_id, data=user)
        GetDataFromUser.set_data_user(user_id=message.from_user.id, data=data_user)

        info = await bot.get_chat(chat_id=transfer_telegram_id)
        await message.answer(data["emojio"] + f" Вы перевели [{info.full_name}](tg://user?id={transfer_telegram_id}) *{transfer_money:,d} $*\nВаш баланс: *{data_user['player_balance']:,d} $*")
        return await bot.send_message(chat_id=transfer_telegram_id, text=data["emojio"] + f' Вам поступил перевод *{transfer_money:,d} $* от [{message.from_user.full_name}](tg://user?id={message.from_user.id})')

    except Exception as e:
        logging.error(e, exc_info=True)
