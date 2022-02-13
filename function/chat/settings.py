import json
import os
import logging

from aiogram import types
from dispatcher import dp, bot
from classes import GetDataFromChat
from function import admin

config = open(os.getcwd() + "/config.json", encoding="UTF-8")
data = json.loads(config.read())
config.close()

@dp.message_handler(commands=['settings', 'panel'])
async def settings_handler(message: types.Message):
    try:
        if message.chat.id == message.from_user.id:
            return

        if not await admin.is_admin_group(chat_id=message.chat.id, user_id=message.from_user.id):
            return

        if not await admin.is_admin_group(chat_id=message.chat.id, user_id=bot.id):
            return

        caption, keyboard = get_settings(chat_id=message.chat.id, full_name=message.chat.full_name)
        return await message.reply(text=caption, reply_markup=keyboard)
        
    except Exception as e:
        logging.error(e, exc_info=True)

def get_settings(chat_id, full_name):
    chat = GetDataFromChat.export_data_from_chat(chat=chat_id)

    caption = data["emojio"] + f" Настройки беседы: {full_name}\n\n"
    caption += f'Упоминание игроков: {( "Выключено ❌" , "Включено ✔" )[ chat["pin_user"] ]}'
    caption += f'Анти КАПС: {( "Выключено ❌" , "Включено ✔" )[ chat["anti_capslock"] ]}'
    caption += f'Анти URL: {( "Выключено ❌" , "Включено ✔" )[ chat["anti_url"] ]}'

    buttons  = [types.InlineKeyboardButton(text=f'Упоминание: {( "Включить" , "Выключить" )[ chat["pin_user"] ]}', callback_data="Упоминание"),
    types.InlineKeyboardButton(text=f'Анти КАПС: {( "Включить" , "Выключить" )[ chat["anti_capslock"] ]}', callback_data="Анти-КАПС"),
    types.InlineKeyboardButton(text=f'Анти URL: {( "Включить" , "Выключить" )[ chat["anti_url"] ]}', callback_data="Анти URL")] 
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)

    return (caption, keyboard)