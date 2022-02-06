import os
import json

from dispatcher import dp, bot
from classes import GetDataFromChat
from . import admin
from . import associations

@dp.message_handler(content_types=["text"])
async def check_all_messages(message):
    try:
        if message.chat.id != message.from_user.id:

            if not GetDataFromChat.is_created_chat(chat=message.chat.id):
                return GetDataFromChat.created_data_chat(chat=message.chat.id)
                
            chat = GetDataFromChat.export_data_from_chat(chat=message.chat.id)

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
                await associations.checking_association(chat_id=message.chat.id,
                    from_user=message.from_user.id,
                    full_name=message.from_user.full_name,
                    text=message.text,
                    message_id=message.message_id)
    except Exception as e:
        print("Messages handlers:", e)