import asyncio
import json
import os
import random
import requests

from aiogram import types
from dispatcher import dp, bot
from classes import GetDataFromChat, GetDataFromUser
from . import admin

from bs4 import BeautifulSoup

config = open(os.getcwd() + "/config.json", encoding="UTF-8")
data = json.loads(config.read())
config.close()

@dp.message_handler(commands=['association'])
async def association_handlers(message: types.Message):
    try:
        if message.from_user.id == message.chat.id:
            return 

        if await admin.is_admin_group(message.chat.id, bot.id):
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

        if not GetDataFromChat.is_created_chat(message.chat.id):
            GetDataFromChat.created_data_chat(message.chat.id)

        chat = GetDataFromChat.export_data_from_chat(chat=message.chat.id)
        if chat["action"] is not None:
            return
        
        with open("games/association.txt", encoding="UTF-8") as file:
            words = file.read()

        splited = words.split(",")

        chat["value"] = random.choice(splited)
        chat["action"] = "Association"
        chat["time"] = data["time_association"]

        parse_words(message.chat.id, chat["value"])
        
        await message.answer(text=data["emojio"] + f' *Ассоциации*\n\n_✏ Пишите ассоциации к слову в течении {data["time_association"]} секунд\n⚡ Зарабатывайте очки и выигрывайте_\n\nСлово для ассоциаций: *{chat["value"]}*')
        GetDataFromChat.import_data_from_chat(chat=message.chat.id, data=chat)
        return await countdown_association(chat_id=message.chat.id)

    except Exception as e:
        print(repr(e))

def parse_words(chat_id, word):
    try:
        url = 'http://sinonim.org/as/%s' % word
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36','Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'})
        soup = BeautifulSoup(response.text, 'lxml')
        #sections = soup.find_all('ul', class_="assocPodryad")
        cases = soup.find_all('li')

        with open("data/chats/" + str(chat_id) + "/words.txt", "+w") as parse:
            for item in cases:
                if "." not in item.get_text():
                    parse.write(item.get_text() + ",")

    except Exception as e:
        print(repr(e))

async def countdown_association(chat_id):
    try:
        if not GetDataFromChat.is_created_chat(chat_id):
            GetDataFromChat.created_data_chat(chat_id)

        chat = GetDataFromChat.export_data_from_chat(chat=chat_id)
        if chat["action"] == "Association":
            chat["time"] -= 5

            if chat["time"] == 60:
                await bot.send_message(chat_id=chat_id, text=data["emojio"] + f' *Ассоциации*\n📌 Напоминаю слово: *{chat["value"]}*\n\nОсталось: *60 секунд..*')

            if chat["time"] == 30:
                await bot.send_message(chat_id=chat_id, text=data["emojio"] + f' *Ассоциации*\n📌 Напоминаю слово: *{chat["value"]}*\n\nОсталось: *30 секунд..*')

            if chat["time"] <= 0:
                return await end_association(chat_id)
                
            GetDataFromChat.import_data_from_chat(chat=chat_id, data=chat)
            await asyncio.sleep(5)
            return await countdown_association(chat_id)

    except Exception as e:
        print(repr(e))

async def checking_association(chat_id, from_user, full_name, text, message_id):
    try:
        chat = GetDataFromChat.export_data_from_chat(chat=chat_id)

        if chat["action"] != "Association":
            return 

        with open(os.getcwd() + "/data/chats/" + str(chat_id) + "/words.txt") as file:
            words = file.read()

        item = words.split(",")
        for temp in item:

            if text.lower() != temp.lower():
                continue

            words.replace(temp + ",", "")
            with open(os.getcwd() + "/data/chats/" + str(chat_id) + "/words.txt", "+w") as file:
                file.write(words)

            score = int(len(text) / 2)
            user = {"name": full_name, "score": score}

            if os.path.isfile(os.getcwd() + "/data/chats/" + str(chat_id) + "/association/" + str(from_user) + ".json"):

                with open(os.getcwd() + "/data/chats/" + str(chat_id) + "/association/" + str(from_user) + ".json", encoding="UTF-8") as file:
                    user = json.loads(file.read())

                user["score"] += score

            with open(os.getcwd() + "/data/chats/" + str(chat_id) + "/association/" + str(from_user) + ".json", "+w", encoding="UTF-8") as file:
                json.dump(user, file, ensure_ascii=False, indent=4)

            await bot.send_message(chat_id=chat_id, reply_to_message_id=message_id, text=data["emojio"] + f' *Ассоциации*\nСлово *{text}* засчитано!\n⚡ *+{score} {ending(score)}*')

    except Exception as e:
        print(repr(e))
    
async def end_association(chat_id):
    try:
        chat = GetDataFromChat.export_data_from_chat(chat=chat_id)
        dirs = os.listdir(os.getcwd() + "/data/chats/" + str(chat_id) + "/association")

        maximum = 0
        message = data["emojio"] + f' *Ассоциации\nИгра закончилась!*\n\nУчастники:\n'
        win_message = ""

        for temp in dirs:
            with open(os.getcwd() + "/data/chats/" + str(chat_id) + "/association/" + temp, encoding="UTF-8") as file:
                user = json.loads(file.read())

            os.remove(os.getcwd() + "/data/chats/" + str(chat_id) + "/association/" + temp)

            user_id = int(temp.replace(".json", ""))
            pin_user = f'[{user["name"]}](tg://user?id={user_id})'

            message += f'{( user["name"] , pin_user )[ chat["pin_user"] ]} - ⚡ {user["score"]} {ending(user["score"])}.\n'

            if user["score"] > maximum:
                win_message = f'\nУ {( user["name"] , pin_user )[ chat["pin_user"] ]} больше всего очков.'

        message += win_message
        await bot.send_message(chat_id=chat_id, text=message)
        GetDataFromChat.remove_game_from_chat(chat_id)
    except Exception as e:
        print(repr(e))

def ending(number):
    if (number % 100) // 10 != 1 and number % 10 == 1 :
        return "очко"
        
    if (number % 100) // 10 != 1 and number % 10 in [2,3,4]:
        return "очка"

    return "очков"