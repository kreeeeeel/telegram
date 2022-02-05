import os
import json
import time

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

@dp.message_handler(commands=['mute'])
async def mute_command(message: types.Message):
    try:
        if message.chat.id == message.from_user.id:
            return await message.answer("🍍 Нужно использовать только в чатах!")

        if not message.reply_to_message:
            return await message.reply("🍍 Команда должна быть использована на ответное сообщение!")

        if not await is_admin_group(message.chat.id, message.bot.id):
            return await bot.send_message(message.chat.id, "🍍 Для полного функционала бота, рекомендуется выдать Администратора.")

        if message.reply_to_message.from_user.id == message.bot.id:
            return await message.reply("🍍 Невозможно использовать команду...")

        if not await is_admin_group(message.chat.id, message.from_user.id):
            return await bot.delete_message(message.chat.id, message.message_id)

        if await is_admin_group(message.chat.id, message.reply_to_message.from_user.id):
            return await message.reply("🍍 [%s](tg://user?id=%d) является *Администратором*" % (message.reply_to_message.from_user.first_name,message.reply_to_message.from_user.id), parse_mode="Markdown")

        await message.answer("🍍 [%s](tg://user?id=%d) *не сможет писать в чат 30 минут*" % (message.reply_to_message.from_user.first_name,message.reply_to_message.from_user.id), parse_mode="Markdown")
        await bot.restrict_chat_member(chat_id=message.chat.id, user_id=message.reply_to_message.from_user.id,until_date=int(time.time()) + 60*30, permissions={'can_send_messages': False})
    except Exception as e:
        print(repr(e))

@dp.message_handler(commands=['kick'])
async def kick_command(message: types.Message):
    try:
        if message.chat.id == message.from_user.id:
            return await message.answer("🍍 Нужно использовать только в чатах!")

        if not message.reply_to_message:
            return await message.reply("🍍 Команда должна быть использована на ответное сообщение!")

        if not await is_admin_group(message.chat.id, message.bot.id):
            return await bot.send_message(message.chat.id, "🍍 Для полного функционала бота, рекомендуется выдать Администратора.")

        if message.reply_to_message.from_user.id == message.bot.id:
            return await message.reply("🍍 Невозможно использовать команду...")

        if not await is_admin_group(message.chat.id, message.from_user.id):
            return await bot.delete_message(message.chat.id, message.message_id)

        if await is_admin_group(message.chat.id, message.reply_to_message.from_user.id):
            return await message.reply("🍍 [%s](tg://user?id=%d) является *Администратором*" % (message.reply_to_message.from_user.first_name,message.reply_to_message.from_user.id), parse_mode="Markdown")

        await bot.delete_message(message.chat.id, message.message_id)
        await message.answer("🍍 [%s](tg://user?id=%d) *кикнул(-а)* [%s](tg://user?id=%d)" % (message.from_user.first_name,message.from_user.id,message.reply_to_message.from_user.first_name,message.reply_to_message.from_user.id), parse_mode="Markdown")
        await bot.kick_chat_member(message.chat.id, message.reply_to_message.from_user.id)
    
    except Exception as e:
        print(repr(e))

@dp.message_handler(commands=['wrapping'])
async def wrapping_handler(message: types.Message):
    try:
        if message.from_user.id != data["develop"]:
            return 

        user = message.from_user.id
        if message.reply_to_message:
            if message.reply_to_message.from_user.id == message.bot.id:
                return

            user = message.reply_to_message.from_user.id
            
        args = message.get_args()
        if not args or not args.isdigit():
            return

        if not GetDataFromUser.is_user_data(user_id=user):
            return 

        value = int(args)
        if value < 0:
            return 

        data_user = GetDataFromUser.get_data_user(user_id=user)
        data_user["player_balance"] += value
        GetDataFromUser.set_data_user(user_id=user, data=data_user)

        if message.from_user.id != user:
            player = await bot.get_chat(chat_id=user)
            await message.answer(text=data["emojio"] + f' Вы увеличили баланс [{player.full_name}](tg://user?id={user}) на *{value} $*')
            return await bot.send_message(chat_id=user, text=data["emojio"] + f" [{message.from_user.full_name}](tg://user?id={message.from_user.id}) увеличил ваш баланс на *{value} $*")

        return await message.answer(text=data["emojio"] + f' Ваш баланс увеличен *{value} $*')

    except Exception as e:
        print(repr(e))