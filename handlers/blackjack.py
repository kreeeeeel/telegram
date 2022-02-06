from ast import parse
import asyncio
import json
import os
import queue
import random

from aiogram import types
from dispatcher import dp, bot
from classes import GetDataFromChat, GetDataFromUser

import asyncio
import json
import os
import random

from aiogram import types
from dispatcher import dp, bot
from classes import GetDataFromChat, GetDataFromUser
from . import admin

config = open(os.getcwd() + "/config.json", encoding="UTF-8")
data = json.loads(config.read())
config.close()

cards = [6, 7, 8, 9, 10, "ВАЛЕТ", "ДАМА", "КОРОЛЬ", "ТУЗ"] * 4

@dp.message_handler(commands=['blackjack'])
async def blackjack_handler(message: types.Message):
    try:
        if message.from_user.id == message.chat.id:
            return 

        if not GetDataFromChat.is_created_chat(message.chat.id):
            GetDataFromChat.created_data_chat(message.chat.id)

        chat = GetDataFromChat.export_data_from_chat(chat=message.chat.id)
        if chat["action"] is not None:
            return

        bet_game = 100
        bet = message.get_args()

        #bet = message.text.split(" ")
        if bet is not None and bet.isdigit():
            if int( bet ) < data["minimal_bet_blackjack"]:
                return await message.reply(f'💰 Минимальная ставка в Блэк-Джек *{data["minimal_bet_blackjack"]}$*')

            bet_game = int( bet )

        if not GetDataFromUser.is_user_data(message.from_user.id):
            GetDataFromUser.create_user_data(message.from_user.id)

        data_user = GetDataFromUser.get_data_user(message.from_user.id)
        if data_user["player_balance"] < bet_game:
            return await message.reply(text="💰 У вас недостаточно средств..")

        if await admin.is_admin_group(message.chat.id, bot.id):
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

        # Generate keyboard
        button_url = f'https://t.me/{data["name"]}?start={message.chat.id}'

        buttons = [types.InlineKeyboardButton(text='Присоединиться', url=button_url)]
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(*buttons)

        value_message = await message.answer(text=data["emojio"] + f' Игра: *Блэк-Джек!\n💰 Ставка: {bet_game} $*\nДля регистрации нажмите:', reply_markup=keyboard)
        massive_message = [{"message_id": value_message.message_id}]

        chat["action"] = "Black-Jack"
        chat["type"] = "Register"
        chat["message"] = massive_message
        chat["hash"] = random.randint(10000,99999)
        chat["time"] = 60
        chat["bet"] = bet_game

        GetDataFromChat.import_data_from_chat(chat=message.chat.id, data=chat)
        return await countdown_blackjack(message.chat.id)

    except Exception as e:
        print("Command blackjack: ", e)

async def edit_blackjack_handler(chat_id):
    try:
        chat = GetDataFromChat.export_data_from_chat(chat=chat_id)
        dirs = os.listdir(os.getcwd() + "/data/chats/" + str(chat_id) + "/blackjack")

        message = data["emojio"] + f' Игра: *Блэк-Джек!*\n💰 *Ставка: {chat["bet"]} $*\n\nУчастники:\n'
        for temp in dirs:
            with open(os.getcwd() + "/data/chats/" + str(chat_id) + "/blackjack/" + temp, encoding="UTF-8") as file:
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
        print("Edit message blackjack: ", e)


async def join_blackjack_handler(user_id, chat_id, full_name):
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

        if chat["action"] == "Black-Jack" and chat["type"] == "Register":

            if chat["bet"] > data_user["player_balance"]:
                return await bot.send_message(chat_id=user_id, text="💰 У вас недостаточно средств..")

            data_blackjack = { "name": full_name, "cards": None }
            with open(os.getcwd() + "/data/chats/" + str(chat_id) + "/blackjack/" + str(user_id) + ".json", "+w", encoding="UTF-8") as file:
                json.dump(data_blackjack, file, ensure_ascii=False, indent=4)

            data_user["player_game"] = chat_id
            data_user["player_balance"] -= chat["bet"]

            GetDataFromUser.set_data_user(user_id, data_user)
            await edit_blackjack_handler(chat_id=chat_id)
            return await bot.send_message(chat_id=user_id, text=data["emojio"] + f' Вы присоединились к игре в [{chat_value.full_name}]({chat_value.invite_link})')
    
    except Exception as e:
        print("Joined BlackJack:" , e)

async def countdown_blackjack(chat_id, forcibly=False):
    try:
        if not GetDataFromChat.is_created_chat(chat_id):
            GetDataFromChat.created_data_chat(chat_id)

        chat = GetDataFromChat.export_data_from_chat(chat=chat_id)
        if chat["action"] == "Black-Jack":
            chat["time"] -= 5

            GetDataFromChat.import_data_from_chat(chat_id, chat)
            if chat["type"] == "Register":

                if forcibly:
                    return await start_blackjack(chat_id)

                if chat["time"] == 30:
                    value = await bot.send_message(chat_id=chat_id, text=data["emojio"] + " До начала игры осталось *30 секунд..*", 
                    reply_to_message_id=chat["message"], parse_mode="Markdown")

                    messages = list(chat["message"])
                    messages.append({"message_id": value.message_id})
                    chat["message"] = messages

                    GetDataFromChat.import_data_from_chat(chat_id, chat)

                if chat["time"] <= 0:
                    await start_blackjack(chat_id)

            if chat["type"] == "Game" and chat["time"] <= 0:
                return await skipped_players(chat_id)

            await asyncio.sleep(5)
            return await countdown_blackjack(chat_id=chat_id)
    except Exception as e:
        print("Countdown BlackJack:" , e)

async def start_blackjack(chat_id):
    try:
        chat = GetDataFromChat.export_data_from_chat(chat=chat_id)
        for temp in chat["message"]:
            try:
                await bot.delete_message(chat_id=chat_id, message_id=temp["message_id"])

            except:
                pass

        dirs = os.listdir(os.getcwd() + "/data/chats/" + str(chat_id) + "/blackjack")
        members = len(dirs)

        if members <= 1:
            for temp in dirs:
                os.remove(os.getcwd() + "/data/chats/" + str(chat_id) + "/blackjack/" + temp)

                profile = GetDataFromUser.get_data_user(int(temp.replace(".json", "")))
                profile["player_game"] = None
                profile["player_balance"] += chat["bet"]
                GetDataFromUser.set_data_user(int(temp.replace(".json", "")), profile)

            GetDataFromChat.remove_game_from_chat(chat_id)
            return await bot.send_message(chat_id=chat_id, text=data["emojio"] + " *Блэк-Джек*\nНедостаточно игроков для начала игры\nДеньги возвращены..", parse_mode="Markdown")

        await bot.send_message(chat_id=chat_id, text=data["emojio"] + " *Диллер*: начинает раздавать карты..", parse_mode="Markdown")
        message = data["emojio"] + f' *Блэк-Джек*\n💰 *Ставка: {chat["bet"]} $*\n_Диллер раздал карты_\n\nКарты участников:\n'

        count = 1
        queue_message = ""

        for temp in dirs:

            with open(os.getcwd() + "/data/chats/" + str(chat_id) + "/blackjack/" + temp, encoding="UTF-8") as file:
                info = json.loads(file.read())

            first_card = random.choice(cards)
            second_card = random.choice(cards)

            pin_user = f'[{info["name"]}](tg://user?id={int(temp.replace(".json", ""))})'

            info["cards"] = [
                {"card": first_card},
                {"card": second_card}
            ]

            with open(os.getcwd() + "/data/chats/" + str(chat_id) + "/blackjack/" + temp, "+w", encoding="UTF-8") as file:
                json.dump(info, file, ensure_ascii=False, indent=4)

            message += f'У {( info["name"] , pin_user )[ chat["pin_user"] ]} карты: {first_card} {second_card} ({value_cards(info["cards"])})\n'

            if count == 1:
                chat["queue"] = int(temp.replace(".json", ""))
                queue_message = f'\n{( info["name"] , pin_user )[ chat["pin_user"] ]} сейчас ваша очередь'

            count += 1

        message += queue_message

        buttons = [
            types.InlineKeyboardButton(text='Взять карту', callback_data=f'get_{chat_id}_{chat["hash"]}'),
            types.InlineKeyboardButton(text='Пропустить', callback_data=f'skip_{chat_id}_{chat["hash"]}')
        ]
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(*buttons)

        value = await bot.send_message(chat_id=chat_id, text=message, reply_markup=keyboard)

        chat["message"] = value.message_id
        chat["type"] = "Game"
        chat["time"] = data["time_blackjack"]
        GetDataFromChat.import_data_from_chat(chat_id, chat)
            
    except Exception as e:
        print("Start BlackJack:" , e)

async def buttons_blackjack(from_id, message_id, action, chat_id, hash):
    try:
        chat = GetDataFromChat.export_data_from_chat(chat=chat_id)
        if chat["action"] != "Black-Jack" or chat["type"] != "Game" or chat["hash"] != int(hash):
            return await bot.delete_message(chat_id=chat_id, message_id=message_id)

        if chat["queue"] != from_id:
            return

        dirs = os.listdir(os.getcwd() + "/data/chats/" + str(chat_id) + "/blackjack")
        if action == "skip":

            temp = str(from_id) + ".json"
            index = dirs.index(temp)

            with open(os.getcwd() + "/data/chats/" + str(chat_id) + "/blackjack/" + temp, encoding="UTF-8") as file:
                info = json.loads(file.read())

            pin_user = f'[{info["name"]}](tg://user?id={int(temp.replace(".json", ""))})'

            await bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=None)
            await bot.send_message(chat_id=chat_id, text=data["emojio"] + f' *Блэк-Джек*\n{( info["name"] , pin_user )[ chat["pin_user"] ]} пропустил.')

            if index + 1 == len(dirs):
                await bot.send_message(chat_id=chat_id, text=data["emojio"] + f" *Блэк-Джек*\n\n_Диллер раскладывает себе карты_.")
                await asyncio.sleep(3)
                return await end_blackjack(chat_id)

            chat["queue"] = int(dirs[index + 1].replace(".json", ""))
            chat["time"] = data["time_blackjack"]
            GetDataFromChat.import_data_from_chat(chat_id, chat)
            return await message_for_blackjack(chat_id=chat_id)

        if action == "get":

            temp = str(from_id) + ".json"
            index = dirs.index(temp)

            with open(os.getcwd() + "/data/chats/" + str(chat_id) + "/blackjack/" + temp, encoding="UTF-8") as file:
                info = json.loads(file.read())

            pin_user = f'[{info["name"]}](tg://user?id={int(temp.replace(".json", ""))})'

            card = info["cards"]

            taken = random.choice(cards)
            card.append({"card": taken})

            info["cards"] = card

            with open(os.getcwd() + "/data/chats/" + str(chat_id) + "/blackjack/" + temp, "+w", encoding="UTF-8") as file:
                json.dump(info, file, ensure_ascii=False, indent=4)

            await bot.send_message(chat_id=chat_id, text=data["emojio"] + f' *Блэк-Джек*\n{( info["name"] , pin_user )[ chat["pin_user"] ]} взял карту {taken}.')

            if value_cards(card) > 21 and index + 1 < len(dirs):
                chat["queue"] = int(dirs[index + 1].replace(".json", ""))

            chat["time"] = data["time_blackjack"]
            GetDataFromChat.import_data_from_chat(chat_id, chat)

            await message_for_blackjack(chat_id=chat_id, message_id=message_id, edit=True)

            if value_cards(card) > 21 and index + 1 == len(dirs):
                await bot.send_message(chat_id=chat_id, text=data["emojio"] + f" *Блэк-Джек*\n\n_Диллер раскладывает себе карты_.")
                await asyncio.sleep(3)
                await bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=None)
                return await end_blackjack(chat_id)

    except Exception as e:
        print("Button blackjack:", e)

async def message_for_blackjack(chat_id, message_id=None, edit=False):
    try:
        chat = GetDataFromChat.export_data_from_chat(chat=chat_id)
        dirs = os.listdir(os.getcwd() + "/data/chats/" + str(chat_id) + "/blackjack")
        message = data["emojio"] + f' *Блэк-Джек*\n💰 *Ставка: {chat["bet"]} $*\n_Диллер раздал карты_\n\nКарты участников:\n'

        for item in dirs:

            with open(os.getcwd() + "/data/chats/" + str(chat_id) + "/blackjack/" + item, encoding="UTF-8") as file:
                info = json.loads(file.read())

            pin_user = f'[{info["name"]}](tg://user?id={int(item.replace(".json", ""))})'
            message += f'У {( info["name"] , pin_user )[ chat["pin_user"] ]} карты: '

            for temp in info["cards"]:
                message += f'{temp["card"]} '

            value = value_cards(info["cards"])
            if value > 21:
                message += "(Перебор)\n"
            else:
                message += f'({value})\n'

            if str(chat["queue"]) + ".json" == item:
                queue_message = f'\n{( info["name"] , pin_user )[ chat["pin_user"] ]} сейчас ваша очередь'

        message += queue_message

        buttons = [
            types.InlineKeyboardButton(text='Взять карту', callback_data=f'get_{chat_id}_{chat["hash"]}'),
            types.InlineKeyboardButton(text='Пропустить', callback_data=f'skip_{chat_id}_{chat["hash"]}')
        ]
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(*buttons)

        if edit and message_id is not None:
            value = await bot.edit_message_text(text=message, chat_id=chat_id, message_id=message_id, reply_markup=keyboard)
        else:
            value = await bot.send_message(chat_id=chat_id, text=message, reply_markup=keyboard)
        chat["message"] = value.message_id
        GetDataFromChat.import_data_from_chat(chat=chat_id, data=chat)

    except Exception as E:
        print("Message for blackjack", E)

async def skipped_players(chat_id):
    try:
        chat = GetDataFromChat.export_data_from_chat(chat=chat_id)
        dirs = os.listdir(os.getcwd() + "/data/chats/" + str(chat_id) + "/blackjack")

        with open(os.getcwd() + "/data/chats/" + str(chat_id) + "/blackjack/" + str(chat["queue"]) + ".json", encoding="UTF-8") as file:
            info = json.loads(file.read())

        pin_user = f'[{info["name"]}](tg://user?id={chat["queue"]})'
        await bot.send_message(chat_id=chat_id, text=data["emojio"] + f' *Блэк-Джек*\n{( info["name"] , pin_user )[ chat["pin_user"] ]} не сделал(-а) ход.')

        index = dirs.index(str(chat["queue"]) + ".json")
        if index + 1 == len(dirs):
            return await end_blackjack(chat_id)

        choise = dirs[index + 1]
        choise = int( choise.replace(".json", "") )
        chat["queue"] = choise
        chat["time"] = data["time_blackjack"]

        GetDataFromChat.import_data_from_chat(chat_id, chat)
        await bot.edit_message_reply_markup(chat_id=chat_id, message_id=chat["message"], reply_markup=None)
        return await message_for_blackjack(chat_id=chat_id)

    except Exception as e:
        print("Skipped player: ", e)

async def end_blackjack(chat_id):
    try:
        chat = GetDataFromChat.export_data_from_chat(chat=chat_id)
        dirs = os.listdir(os.getcwd() + "/data/chats/" + str(chat_id) + "/blackjack")
        message = data["emojio"] + f' *Блэк-Джек*\n💰 *Ставка: {chat["bet"]} $\nИгра окончена!*\n\n_Диллер раскрывал свои карты_\n\nКарты участников:\n'

        card = [{"card": random.choice(cards)}, {"card": random.choice(cards)}]
        value_diller = value_cards(card)

        for item in dirs:
            user_id = int(item.replace(".json", ""))
            data_user = GetDataFromUser.get_data_user(user_id)
            data_user["player_game"] = None

            with open(os.getcwd() + "/data/chats/" + str(chat_id) + "/blackjack/" + item, encoding="UTF-8") as file:
                info = json.loads(file.read())

            pin_user = f'[{info["name"]}](tg://user?id={int(item.replace(".json", ""))})'
            message += f'У {( info["name"] , pin_user )[ chat["pin_user"] ]} карты: '

            for temp in info["cards"]:
                message += f'{temp["card"]} '

            value = value_cards(info["cards"])
            if value > 21:
                message += "(Перебор)\n"

            elif value > value_diller:
                message += "(Победа)\n"
                data_user["player_balance"] += chat["bet"] * 2
                GetDataFromUser.give_referal_money(user_id=data_user["player_invited"], ammount=chat["bet"] * 2)

            elif value == value_diller:
                message += "(Ничья)\n"
                data_user["player_balance"] += chat["bet"]

            else:
                message += "(Проигрышь)\n"

            GetDataFromUser.set_data_user(user_id=user_id, data=data_user)
            os.remove(os.getcwd() + "/data/chats/" + str(chat_id) + "/blackjack/" + item)

        message += f'\nКарты диллера: {card[0]["card"]} {card[1]["card"]} ({value_diller})'
        await bot.send_message(text=message, chat_id=chat_id)
        return GetDataFromChat.remove_game_from_chat(chat_id)

    except Exception as E:
        print("end for blackjack", E)

def value_cards(cards):

    value = 0
    checking = []
    
    for temp in cards:

        card = temp["card"]
        checking.append(card)

        if card == "ТУЗ":
            value += 11

        elif card == "КОРОЛЬ" or card == "ВАЛЕТ" or card == "ДАМА":
            value += 10

        else:
            value += card

        if value > 21 and "А" in checking:
            value -= 10

    return value
