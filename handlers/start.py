import json
import os

from aiogram import types
from dispatcher import dp, bot
from . import mafia
from . import blackjack
from classes import GetDataFromChat, GetDataFromUser

config = open(os.getcwd() + "/config.json", encoding="UTF-8")
data = json.loads(config.read())
config.close()

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    try:
        value = message.get_args()
        if message.from_user.id == message.chat.id:

            if value:

                value = int(value)
                if GetDataFromUser.is_user_data(user_id=value):

                    if GetDataFromUser.is_user_data(user_id=message.from_user.id):
                        return await message.reply(text=data["emojio"] + " Невозможно присоединиться по реферальной ссылке\nТак как вы уже зарегистрированы..")

                    user = GetDataFromUser.get_data_user(user_id=value)
                    appened = [{"user": message.from_user.id}]
                    referals = user["player_referals"]
                    if user["player_referals"] is None:
                        referals = appened

                    if user["player_referals"] is not None:
                        referals = list(user["player_referals"])
                        referals.append({"user": message.from_user.id})

                    user["player_referals"] = referals
                    user["player_referal_balance"] += data["bonus_referal"] * user["player_referal_lvl"]
                    GetDataFromUser.set_data_user(user_id=value, data=user)

                    referal_info = await bot.get_chat(chat_id=value)

                    caption = data["emojio"] + f' Вы перешли по реферальной ссылке от [{referal_info.full_name}](tg://user?id={value})'
                    if data["bonus_referal"] * user["player_referal_lvl"] > 0:
                        caption += f'\n💰 Вы получили бонус: *{data["bonus_referal"] * user["player_referal_lvl"]}$ *'

                    await message.answer(text=caption)

                    caption = data["emojio"] + f' [{message.from_user.full_name}](tg://user?id={message.from_user.id}) перешёл(-а) по вашей ссылке.'
                    if data["bonus_referal"] * user["player_referal_lvl"] > 0:
                        caption += f'\n💰 Вы получили бонус: *{data["bonus_referal"] * user["player_referal_lvl"]}$ *'

                    await bot.send_message(chat_id=value, text=caption, parse_mode="Markdown")

                    return GetDataFromUser.create_user_data(user_id=message.from_user.id, referal=value, Money=data["bonus_referal"] * user["player_referal_lvl"])
                    
                if not GetDataFromChat.is_created_chat(value):
                    return

                chat = GetDataFromChat.export_data_from_chat(chat=value)
                if chat["action"] == "Mafia":
                    return await mafia.join_mafia_handler(message.from_user.id, value, message.from_user.full_name)

                if chat["action"] == "Black-Jack":
                    return await blackjack.join_blackjack_handler(message.from_user.id, value, message.from_user.full_name)

            if not GetDataFromUser.is_user_data(user_id=message.from_user.id):
                GetDataFromUser.create_user_data(user_id=message.from_user.id)

        buttons  = [types.InlineKeyboardButton(text='Команды 📌', callback_data="Команды")] 
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(*buttons)

        return await message.answer("Приветствую - я Ананасыч 🍍\nМногоспособный бот для веселья!", reply_markup=keyboard)
            

    except Exception as e:
        print("Не удалось обработать команду: ", e)