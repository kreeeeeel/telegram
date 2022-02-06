import asyncio
import logging
import os
import json
import random

from aiogram import types
from dispatcher import dp, bot
from classes import GetDataFromChat , GetDataFromUser

from . import admin

config = open(os.getcwd() + "/config.json", encoding="UTF-8")
data = json.loads(config.read())
config.close()

@dp.message_handler(commands=['double'])
async def double_handler(message: types.Message):
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

        factor = random.randint(0, 100)
        if factor == 100:
            multiplier = "x50"
        
        if factor > 0 and factor <= 10:
            multiplier = "x5"

        if factor > 10 and factor <= 50:
            multiplier = "x3"

        if factor > 50 and factor <= 99:
            multiplier = "x2"

        chat["action"] = "Double"
        chat["value"] = multiplier
        chat["time"] = 60

        GetDataFromChat.import_data_from_chat(chat=message.chat.id, data=chat)
        await message.answer(text=data["emojio"] + " *Дабл\nПринимаем ставки*\n\n_Для участия, делайте свои ставки\nПозиции: X2, X3, X5, X50_\n\n*Ставка: /bet [позиция] [сумма]*")
        await countdown_double(message.chat.id)
    except Exception as e:
        logging.exception("message")

@dp.message_handler(commands=['bet'])
async def bet_handler(message: types.Message):
    try:
        if message.from_user.id == message.chat.id:
            return 

        if not GetDataFromChat.is_created_chat(message.chat.id):
            GetDataFromChat.created_data_chat(message.chat.id)

        chat = GetDataFromChat.export_data_from_chat(chat=message.chat.id)
        if chat["action"] != "Double" or chat["type"] == "No-bet":
            return

        if not GetDataFromUser.is_user_data(message.from_user.id):
            #GetDataFromUser.create_user_data(message.from_user.id)
            return

        data_user = GetDataFromUser.get_data_user(message.from_user.id)

        splited = message.get_args()
        splited = splited.split(" ")
        # 1 - position
        # 2 - bet
        if len(splited) != 2:
            return await message.reply(data["emojio"] + " *Дабл\nИспользуйте: /bet [позиция] [сумма]*")

        if splited[0].lower() != "x2" and splited[0].lower() != "x3" and splited[0].lower() != "x5" and splited[0].lower() != "x50":
            return await message.reply(data["emojio"] + " *Дабл\nИспользуйте: /bet [позиция] [сумма]*")

        if not splited[1].isdigit() and splited[1].lower() != "всё" and splited[1].lower() != "все" and splited[1].lower() != "all":
            return await message.reply(data["emojio"] + " *Дабл\nИспользуйте: /bet [позиция] [сумма]*")

        position = splited[0].lower()
        if splited[1].isdigit():
            bet = int(splited[1])
        else:
            bet = data_user["player_balance"]

        if bet < data["minimal_bet_double"]:
            return await message.reply(f'💰 Минимальная ставка в Дабл *{data["minimal_bet_double"]}$*')

        if data_user["player_balance"] < bet:
            return await message.reply(text="💰 У вас недостаточно средств..")

        data_user["player_balance"] -= bet
        user = {"name": message.from_user.full_name, "bet": bet}
        if os.path.isfile(os.getcwd() + "/data/chats/" + str(message.chat.id) + "/double/" + position + "/" + str(message.from_user.id) + ".json"):
            with open(os.getcwd() + "/data/chats/" + str(message.chat.id) + "/double/" + position + "/" + str(message.from_user.id) + ".json", encoding="UTF-8") as file:
                user = json.loads(file.read())

            user["bet"] += bet

        with open(os.getcwd() + "/data/chats/" + str(message.chat.id) + "/double/" + position + "/" + str(message.from_user.id) + ".json", "+w", encoding="UTF-8") as file:
            json.dump(user, file, ensure_ascii=False, indent=4)

        GetDataFromUser.set_data_user(user_id=message.from_user.id, data=data_user)
        return await message.reply(data["emojio"] + " *Дабл\nВаша ставка была принята.*")

    except Exception as e:
        logging.exception("message")

async def countdown_double(chat_id, forcibly=False):
    try:
        if not GetDataFromChat.is_created_chat(chat_id):
            GetDataFromChat.created_data_chat(chat_id)

        chat = GetDataFromChat.export_data_from_chat(chat=chat_id)
        if chat["action"] == "Double":
            chat["time"] -= 5

            if forcibly:
                return await end_double(chat_id)

            if chat["time"] <= 0:
                return await end_double(chat_id)

            if chat["time"] == 30:
                await bot.send_message(chat_id=chat_id, text=data["emojio"] + " *Дабл\nДо окончания приёма ставок осталось 30 секунд..*")

            if chat["time"] == 10:
                chat["type"] = "No-bet"

                await bot.send_message(chat_id=chat_id, text=data["emojio"] + " *Дабл\nДо окончания осталось 10 секунд\nСтавки не принимаются..*")

            GetDataFromChat.import_data_from_chat(chat_id, chat)
            await asyncio.sleep(5)
            return await countdown_double(chat_id, forcibly)
    except Exception as e:
        logging.exception("message")

async def end_double(chat_id):
    try:
        chat = GetDataFromChat.export_data_from_chat(chat=chat_id)

        positons = [2, 3, 5, 50]

        count_player = 0
        count_win = 0
        ammount_money = 0

        message = data["emojio"] + f' *Дабл\nПодсчёт окончен\nОбщий банк: {ammount_money} $*\n'

        for item in positons:
            dirs = os.listdir(os.getcwd() + "/data/chats/" + str(chat_id) + "/double/x" + str(item))
            for temp in dirs:
                with open(os.getcwd() + "/data/chats/" + str(chat_id) + "/double/x" + str(item) + "/" + temp, encoding="UTF-8") as file:
                    user = json.loads(file.read())

                os.remove(os.getcwd() + "/data/chats/" + str(chat_id) + "/double/x" + str(item) + "/" + temp)

                user_id = int(temp.replace(".json", ""))
                pin_user = f'[{user["name"]}](tg://user?id={user_id})'
                ammount_money += user["bet"]

                if chat["value"] == "x" + str(item):
                    message += "✅ "

                    data_user = GetDataFromUser.get_data_user(user_id)
                    data_user["player_balance"] += user["bet"] * item

                    GetDataFromUser.set_data_user(user_id, data_user)
                    GetDataFromUser.give_referal_money(user_id=data_user["player_invited"], ammount=user["bet"] * item)
                    count_win += 1

                else:
                    message += "❌ "

                message += f'{( user["name"] , pin_user )[ chat["pin_user"] ]} - {user["bet"]} $ - X{item}\n'

        message += f'\n_Кол-во ставок: {count_player}\nВыигрышных: {count_win}_'

        GetDataFromChat.remove_game_from_chat(chat_id)

        image = open(os.getcwd() + "/games/" + chat["value"] + ".jpg", "rb")
        return await bot.send_photo(chat_id=chat_id, caption=message, photo=image)

    except Exception as e:
        logging.exception("message")
