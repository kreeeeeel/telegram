import logging

from aiogram import types
from dispatcher import dp, bot
from classes import GetDataFromChat

@dp.message_handler(content_types=["left_chat_member"])
async def new_chat_handler(message: types.Message):
    try:
        if message.left_chat_member.id != bot.id:
            return 
            
        return GetDataFromChat.remove_bot_chat(message.chat.id)

    except Exception as e:
        logging.error(e, exc_info=True)