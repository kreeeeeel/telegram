import os
import json
import logging

from aiogram import types
from dispatcher import dp, bot
from classes import GetDataFromChat

config = open(os.getcwd() + "/config.json", encoding="UTF-8")
data = json.loads(config.read())
config.close()

@dp.message_handler(content_types=["new_chat_members"])
async def new_chat_handler(message):
    try:
        if message.new_chat_members[0].id != bot.id:
            return 

        if not GetDataFromChat.is_created_chat(message.chat.id):
            GetDataFromChat.created_data_chat(message.chat.id)
            
        caption = data["emojio"] + f" Приветствую вас, моё имя *{data['name_rus']}*\n"
        caption += "Я вроде как считаюсь игровый ботом\n"
        caption += 'Для запуск функционала бота требуются:\n'
        caption += '📌 _Права администратора_\n\n'
        caption += 'После выдачи прав, нажмите кнопку *Проверить*'

        buttons  = [types.InlineKeyboardButton(text='Проверить', callback_data="Проверить")] 
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(*buttons)

        return await bot.send_message(chat_id=message.chat.id, text=caption, reply_markup=keyboard)

    except Exception as e:
        logging.error(e, exc_info=True)
