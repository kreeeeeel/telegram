import os
import json
import logging

from dispatcher import dp, bot
from classes import GetDataFromChat, GetDataFromUser
from function import admin
from function.games import associations, crocodile

@dp.message_handler(content_types=["text"])
async def check_all_messages(message):
    try:
        if message.chat.id != message.from_user.id:

            if not GetDataFromChat.is_created_chat(chat=message.chat.id):
                return GetDataFromChat.created_data_chat(chat=message.chat.id)
                
            chat = GetDataFromChat.export_data_from_chat(chat=message.chat.id)
            if not chat["working"]:
                return 
            
            if chat["anti_capslock"] and message.text == message.text.upper() and await admin.is_admin_group(message.chat.id, bot.id):
                await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

            if chat["action"] == "Mafia":
                if not await admin.is_admin_group(message.chat.id, message.from_user.id):
                    return 

                if chat["type"] == "Night":
                    return await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

                if chat["type"] != "Night" and chat["type"] != "Register":
                    dirs = os.listdir(os.getcwd() + "/data/chats/" + str(message.chat.id) + "/mafia")
                    json_file = str(message.from_user.id) + ".json"
                    if json_file in dirs:
                        with open(os.getcwd() + "/data/chats/" + str(message.chat.id) + "/mafia/" + json_file, encoding="UTF-8") as file:
                            user = json.loads(file.read())

                        if not user["alive"]:
                            return await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

            if chat["action"] == "Association":
                return await associations.checking_association(chat_id=message.chat.id,
                    from_user=message.from_user.id,
                    full_name=message.from_user.full_name,
                    text=message.text,
                    message_id=message.message_id)

            if chat["action"] == "Crocodile" and chat["type"] == "Game":
                return await crocodile.guess_the_word(chat_id=message.chat.id, 
                user_id=message.from_user.id, 
                full_name=message.from_user.full_name, 
                text=message.text, 
                message_id=message.message_id)

        if message.from_user.id == message.chat.id:
            if not GetDataFromUser.is_user_data(message.from_user.id):
                GetDataFromUser.create_user_data(message.from_user.id)

            data_user = GetDataFromUser.get_data_user(message.from_user.id)
            if data_user["player_game"] is None:
                return

            chat = GetDataFromChat.export_data_from_chat(chat=data_user["player_game"])
            if chat["queue"] == str(message.from_user.id) + ".json":
                return await crocodile.checking_word(chat_id=data_user["player_game"], user_id=message.from_user.id, text=message.text)
    except Exception as e:
        logging.error(e, exc_info=True)