import asyncio
import json
import os
import random
import logging

from aiogram import types
from dispatcher import dp, bot
from classes import GetDataFromChat, GetDataFromUser
from function import admin

import pymorphy2
morph = pymorphy2.MorphAnalyzer()

config = open(os.getcwd() + "/config.json", encoding="UTF-8")
data = json.loads(config.read())
config.close()

@dp.message_handler(commands=['crocodile'])
async def crocodile_handler(message: types.Message):
    try:
        if message.from_user.id == message.chat.id:
            return 

        if await admin.is_admin_group(message.chat.id, bot.id):
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

        if not GetDataFromChat.is_created_chat(message.chat.id):
            GetDataFromChat.created_data_chat(message.chat.id)

        chat = GetDataFromChat.export_data_from_chat(chat=message.chat.id)
        if not chat["working"]:
            return 
            
        if chat["action"] is not None:
            return

        # Generate keyboard
        button_url = f'https://t.me/{data["name"]}?start={message.chat.id}'

        buttons = [types.InlineKeyboardButton(text='Присоединиться', url=button_url)]
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(*buttons)

        value_message = await message.answer(text=data["emojio"] + " Игра: *Крокодил!*\nДля регистрации нажмите:", reply_markup=keyboard)
        massive_message = [{"message_id": value_message.message_id}]

        chat["action"] = "Crocodile"
        chat["type"] = "Register"
        chat["message"] = massive_message
        chat["time"] = 60

        GetDataFromChat.import_data_from_chat(chat=message.chat.id, data=chat)
        return await countdown_crocodile(message.chat.id)

    except Exception as e:
        logging.error(e, exc_info=True)

async def edit_crocodile_handler(chat_id):
    try:
        chat = GetDataFromChat.export_data_from_chat(chat=chat_id)
        dirs = os.listdir(os.getcwd() + "/data/chats/" + str(chat_id) + "/crocodile")

        message = data["emojio"] + " Игра: *Крокодил!*\n\nУчастники:\n"
        for temp in dirs:
            with open(os.getcwd() + "/data/chats/" + str(chat_id) + "/crocodile/" + temp, encoding="UTF-8") as file:
                info = json.loads(file.read())

            pin_user = f'[{info["name"]}](tg://user?id={temp.replace(".json", "")})'
            message += ( info["name"] , pin_user )[ chat["pin_user"] ] + "\n"

        message += f'\nВсего: {len(dirs)} чел.'

        button_url = f'https://t.me/{data["name"]}?start={chat_id}'

        buttons = [types.InlineKeyboardButton(text='Присоединиться', url=button_url)]
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(*buttons)
        return await bot.edit_message_text(text=message, chat_id=chat_id, message_id=chat["message"][0]["message_id"], reply_markup=keyboard)

    except Exception as e:
        logging.error(e, exc_info=True)


async def join_crocodile_handler(user_id, chat_id, full_name):
    try:
        if not GetDataFromUser.is_user_data(user_id):
            GetDataFromUser.create_user_data(user_id)

        data_user = GetDataFromUser.get_data_user(user_id)
        if data_user["player_game"] is not None:
            return await bot.send_message(chat_id=user_id, text=data["emojio"] + f' Вы принимаете участие в другой игре')
            
        if not GetDataFromChat.is_created_chat(chat_id):
            return

        chat = GetDataFromChat.export_data_from_chat(chat=chat_id)
        chat_value = await bot.get_chat(chat_id=chat_id)

        if chat["action"] == "Crocodile" and chat["type"] == "Register":
            data_crocodile = {
                "name": full_name
            }
            with open("data/chats/" + str(chat_id) + "/crocodile/" + str(user_id) + ".json", "+w", encoding="UTF-8") as file:
                json.dump(data_crocodile, file, ensure_ascii=False, indent=4)

            data_user["player_game"] = chat_id
            GetDataFromUser.set_data_user(user_id, data_user)
            await edit_crocodile_handler(chat_id=chat_id)
            return await bot.send_message(chat_id=user_id, text=data["emojio"] + f' Вы присоединились к игре в [{chat_value.full_name}]({chat_value.invite_link})')
    
    except Exception as e:
        logging.error(e, exc_info=True)

async def countdown_crocodile(chat_id, forcibly=False):
    try:
        if not GetDataFromChat.is_created_chat(chat_id):
            GetDataFromChat.created_data_chat(chat_id)

        chat = GetDataFromChat.export_data_from_chat(chat=chat_id)
        if chat["action"] == "Crocodile":
            chat["time"] -= 5

            GetDataFromChat.import_data_from_chat(chat_id, chat)
            if chat["type"] == "Register":

                if forcibly:
                    return await start_game(chat_id)

                if chat["time"] == 30:
                    value = await bot.send_message(chat_id=chat_id, text=data["emojio"] + " До начала игры осталось *30 секунд..*", 
                    reply_to_message_id=chat["message"], parse_mode="Markdown")

                    messages = list(chat["message"])
                    messages.append({"message_id": value.message_id})
                    chat["message"] = messages

                    GetDataFromChat.import_data_from_chat(chat_id, chat)

                if chat["time"] <= 0:
                    await start_game(chat_id)

            if chat["type"] == "Create word" and chat["time"] <= 0:
                return await delete_game(chat_id)

            if chat["type"] == "Wait" and chat["time"] <= 0:
                return await delete_game(chat_id=chat_id, remove=True)

            await asyncio.sleep(5)
            return await countdown_crocodile(chat_id=chat_id)
    except Exception as e:
        logging.error(e, exc_info=True)

async def start_game(chat_id, queue=None):
    try:
        chat = GetDataFromChat.export_data_from_chat(chat=chat_id)

        for temp in chat["message"]:
            try:
                await bot.delete_message(chat_id=chat_id, message_id=temp["message_id"])

            except:
                pass
        
        dirs = os.listdir(os.getcwd() + "/data/chats/" + str(chat_id) + "/crocodile")
        members = len(dirs)

        if members < 1:
            for temp in dirs:
                os.remove(os.getcwd() + "/data/chats/" + str(chat_id) + "/crocodile/" + temp)

                profile = GetDataFromUser.get_data_user(int(temp.replace(".json", "")))
                profile["player_game"] = None
                GetDataFromUser.set_data_user(int(temp.replace(".json", "")), profile)

            GetDataFromChat.remove_game_from_chat(chat_id)
            return await bot.send_message(chat_id=chat_id, text=data["emojio"] + " *Крокодил*\nНедостаточно игроков для начала игры..")

        if queue is None:
            chat["queue"] = random.choice(dirs)
        chat["type"] = "Create word"
        chat["time"] = 30

        GetDataFromChat.import_data_from_chat(chat_id, chat)

        with open(os.getcwd() + "/data/chats/" + str(chat_id) + "/crocodile/" + chat["queue"], encoding="UTF-8") as file:
            data_user = json.loads(file.read())

        pin_user = f'[{data_user["name"]}](tg://user?id={int(chat["queue"].replace(".json", ""))})'

        await bot.send_message(chat_id=int(chat["queue"].replace(".json", "")), text=data["emojio"] + " Придумайте слово для игры..")

        message = data["emojio"]  + ' *Крокодил*\nИгра началась..\n\n'
        message += f'📌 *Ведущий:* {( data_user["name"] , pin_user )[ chat["pin_user"] ]}\n'
        message += '_Ведущий должен придумать слово, и указать его мне_\n\n'
        message += '⌛ Время: *30 секунд..*'
        return await bot.send_message(chat_id=chat_id, text=message)

    except Exception as e:
        logging.error(e, exc_info=True)

async def delete_game(chat_id, remove=False):
    try:
        chat = GetDataFromChat.export_data_from_chat(chat=chat_id)

        for temp in chat["message"]:
            try:
                await bot.delete_message(chat_id=chat_id, message_id=temp["message_id"])

            except:
                pass
            
        dirs = os.listdir(os.getcwd() + "/data/chats/" + str(chat_id) + "/crocodile")
        for temp in dirs:
            os.remove(os.getcwd() + "/data/chats/" + str(chat_id) + "/crocodile/" + temp)

            profile = GetDataFromUser.get_data_user(int(temp.replace(".json", "")))
            profile["player_game"] = None
            GetDataFromUser.set_data_user(int(temp.replace(".json", "")), profile)

        GetDataFromChat.remove_game_from_chat(chat_id)
        if not remove: 
            return await bot.send_message(chat_id=chat_id, text=data["emojio"] + " *Крокодил*\nИгра была завершена, так как *Ведущий* не придумал слово..")
        return await bot.send_message(chat_id=chat_id, text=data["emojio"] + " *Крокодил*\nИгра была завершена.")
    except Exception as e:
        logging.error(e, exc_info=True)

async def checking_word(chat_id, user_id, text):
    try:
        chat = GetDataFromChat.export_data_from_chat(chat=chat_id)
        parsed = morph.parse( text )
        if 'NOUN' in parsed[0].tag.POS:

            chat["value"] = text
            chat["time"] = 120
            chat["type"] = "Game"

            GetDataFromChat.import_data_from_chat(chat_id, chat)
            await bot.send_message(chat_id=user_id, text=data["emojio"] + f"*Крокодил* \n*{text}* было загадоно!\nИгра началась!")
            return await bot.send_message(chat_id=chat_id, text=data["emojio"] + f' *Крокодил* \nВедущий придумал слово!\nСлово состоит из *{len(text)}* букв.')
        
        return await bot.send_message(chat_id=user_id, text=data["emojio"] + " Слово должно быть существительным!")
    except Exception as e:
        logging.error(e, exc_info=True)

async def guess_the_word(chat_id, user_id, full_name, text, message_id):
    try:
        chat = GetDataFromChat.export_data_from_chat(chat=chat_id)
        dirs = os.listdir(os.getcwd() + "/data/chats/" + str(chat_id) + "/crocodile")
        if chat["queue"] == user_id:
            return await bot.delete_message(chat_id=chat_id, message_id=message_id)

        if chat["value"].lower() == text.lower():
            pin_user = f'[{full_name}](tg://user?id={user_id})'
            message = data["emojio"] + f' *Крокодил*\n*{( full_name , pin_user )[ chat["pin_user"] ]} отгадал слово!*\n\n_Игра будет завершена через_ *30 секунд*\n_Продолжаем?_'

            buttons  = [types.InlineKeyboardButton(text=f'Продолжить (0/{len(dirs)})', callback_data="Команды")] 
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(*buttons)

            chat["type"] = "Wait"
            chat["value"] = None
            chat["time"] = 30
            chat["queue"] = str(user_id) + ".json"

            value = await bot.send_message(chat_id=chat_id, reply_to_message_id=message_id, text=message, reply_markup=keyboard)
            chat["message"] = [{"message_id": value.message_id}]

            GetDataFromChat.import_data_from_chat(chat_id, chat)
    except Exception as e:
        logging.error(e, exc_info=True)

async def keyboard_wait(chat_id, user_id, message_id):
    try:
        if not os.path.isfile(os.getcwd() + "/data/chats/" + str(chat_id) + "/crocodile/" + str(user_id) + ".json"):
            return 

        chat = GetDataFromChat.export_data_from_chat(chat=chat_id)
        if chat["value"] is None:
            chat["value"] = [{"user": user_id}]
        else:
            chat["value"].append({"user": user_id})

        dirs = os.listdir(os.getcwd() + "/data/chats/" + str(chat_id) + "/crocodile")
        members = len(chat["value"])
        keyboard = None

        if len(dirs) != members:
            buttons  = [types.InlineKeyboardButton(text=f'Продолжить ({members}/{len(dirs)})', callback_data="Продолжить")] 
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(*buttons)
            return await bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=keyboard)

        await start_game(chat_id=chat_id, queue=chat["queue"])
        return await bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=None)

    except Exception as e:
        logging.error(e, exc_info=True)
