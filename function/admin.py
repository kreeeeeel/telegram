import os
import json
import time
import logging

from aiogram import types
from dispatcher import dp, bot

from classes import GetDataFromUser

config = open(os.getcwd() + "/config.json", encoding="UTF-8")
data = json.loads(config.read())
config.close()

async def is_admin_group(chat_id, user_id):
    result = await bot.get_chat_member(chat_id, user_id)
    if result["status"] == "administrator" or result["status"] == "creator":
        return True

    return False

@dp.message_handler(commands=['wrapping'])
async def wrapping_handler(message: types.Message):
    try:
        if not GetDataFromUser.is_user_data(user_id=message.from_user.id):
            return 

        admin = GetDataFromUser.get_data_user(user_id=message.from_user.id)
        if admin["player_admin"] is None:
            return

        if message.from_user.id != data["develop"]:
            return 
            
        args = message.get_args()
        if not args or not args.isdigit():
            return

        value = int(args)
        if value < 0:
            return 

        user = message.from_user.id
        if message.reply_to_message:
            if message.reply_to_message.from_user.id == message.bot.id:
                return

            user = message.reply_to_message.from_user.id

        if not GetDataFromUser.is_user_data(user_id=user):
            return 
            
        data_user = GetDataFromUser.get_data_user(user_id=user)
        data_user["player_balance"] += value
        GetDataFromUser.set_data_user(user_id=user, data=data_user)

        if message.from_user.id != user:
            player = await bot.get_chat(chat_id=user)
            await message.answer(text=data["emojio"] + f' Вы увеличили баланс [{player.full_name}](tg://user?id={user}) на *{value:,d} $*')
            return await bot.send_message(chat_id=user, text=data["emojio"] + f" [{message.from_user.full_name}](tg://user?id={message.from_user.id}) увеличил ваш баланс на *{value:,d} $*")

        return await message.reply(text=data["emojio"] + f' Ваш баланс увеличен на *{value:,d} $*')

    except Exception as e:
        logging.error(e, exc_info=True)

@dp.message_handler(commands=['setadmin'])
async def setadmin_handler(message: types.Message):
    try:
        if message.from_user.id != data["develop"] or not message.reply_to_message:
            return

        if not GetDataFromUser.is_user_data(user_id=message.reply_to_message.from_user.id):
            GetDataFromUser.create_user_data(user_id=message.reply_to_message.from_user.id)   

        data_user = GetDataFromUser.get_data_user(user_id=message.reply_to_message.from_user.id)
        data_user["player_admin"] = True
        GetDataFromUser.set_data_user(user_id=message.reply_to_message.from_user.id, data=data_user)
        await message.reply(data["emojio"] + f" Права доступа [{message.reply_to_message.from_user.full_name}](tg://user?id={message.reply_to_message.from_user.id}) выданы.")

    except Exception as e:
        logging.error(e, exc_info=True)

@dp.message_handler(commands=['info'])
async def info_handler(message: types.Message):
    try:
        if message.from_user.id != data["develop"]:
            return

        chats = os.listdir(os.getcwd() + "/data/chats")
        users = os.listdir(os.getcwd() + "/data/users")
        await message.reply(data["emojio"] + f" Бесед: *{len(chats)}*\nПользователей: *{len(users)}*")

    except Exception as e:
        logging.error(e, exc_info=True)
