import asyncio
import json
import os
import random

from aiogram import types
from dispatcher import dp, bot
from classes import GetDataFromChat, GetDataFromUser

from function import admin

config = open(os.getcwd() + "/config.json", encoding="UTF-8")
data = json.loads(config.read())
config.close()

@dp.message_handler(commands=['mafia'])
async def mafia_handler(message: types.Message):
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

        # Generate keyboard
        button_url = f'https://t.me/{data["name"]}?start={message.chat.id}'

        buttons = [types.InlineKeyboardButton(text='Присоединиться', url=button_url)]
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(*buttons)

        value_message = await message.answer(text=data["emojio"] + " Игра: *Мафия!*\nДля регистрации нажмите:", reply_markup=keyboard)
        massive_message = [{"message_id": value_message.message_id}]

        chat["action"] = "Mafia"
        chat["type"] = "Register"
        chat["message"] = massive_message
        chat["hash"] = random.randint(10000,99999)
        chat["time"] = 60

        GetDataFromChat.import_data_from_chat(chat=message.chat.id, data=chat)
        return await countdown_mafia(message.chat.id)

    except Exception as e:
        print("Command mafia: ", e)

async def edit_mafia_handler(chat_id):
    try:
        chat = GetDataFromChat.export_data_from_chat(chat=chat_id)
        dirs = os.listdir(os.getcwd() + "/data/chats/" + str(chat_id) + "/mafia")

        message = data["emojio"] + " Игра: *Мафия!*\n\nУчастники:\n"
        for temp in dirs:
            with open(os.getcwd() + "/data/chats/" + str(chat_id) + "/mafia/" + temp, encoding="UTF-8") as file:
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
        print("Edi message mafia: ", e)


async def join_mafia_handler(user_id, chat_id, full_name):
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

        if chat["action"] == "Mafia" and chat["type"] == "Register":
            data_mafia = {
                "name": full_name,
                "role": None,
                "alive": None,
                "choise": None
            }
            with open("data/chats/" + str(chat_id) + "/mafia/" + str(user_id) + ".json", "+w", encoding="UTF-8") as file:
                json.dump(data_mafia, file, ensure_ascii=False, indent=4)

            data_user["player_game"] = chat_id
            GetDataFromUser.set_data_user(user_id, data_user)
            await edit_mafia_handler(chat_id=chat_id)
            return await bot.send_message(chat_id=user_id, text=data["emojio"] + f' Вы присоединились к игре в [{chat_value.full_name}]({chat_value.invite_link})')
    
    except Exception as e:
        print("Joined Mafia:" , e)

async def countdown_mafia(chat_id, forcibly=False):
    try:
        if not GetDataFromChat.is_created_chat(chat_id):
            GetDataFromChat.created_data_chat(chat_id)

        chat = GetDataFromChat.export_data_from_chat(chat=chat_id)
        if chat["action"] == "Mafia":
            chat["time"] -= 5

            GetDataFromChat.import_data_from_chat(chat_id, chat)
            if chat["type"] == "Register":

                if forcibly:
                    return await distribution_roles(chat_id)

                if chat["time"] == 30:
                    value = await bot.send_message(chat_id=chat_id, text=data["emojio"] + " До начала игры осталось *30 секунд..*", 
                    reply_to_message_id=chat["message"], parse_mode="Markdown")

                    messages = list(chat["message"])
                    messages.append({"message_id": value.message_id})
                    chat["message"] = messages

                    GetDataFromChat.import_data_from_chat(chat_id, chat)

                if chat["time"] <= 0:
                    await distribution_roles(chat_id)

            await checking_alive_user(chat_id)

            if chat["type"] == "Night" and chat["time"] <= 0:
                await setup_morning(chat_id, chat["day"])

            if chat["type"] == "Morning" and chat["time"] <= 0:
                await setup_day(chat_id, chat["day"])

            if chat["type"] == "Day" and chat["time"] <= 0:
                await count_votes(chat_id, chat["day"])

            if chat["type"] == "Voted" and chat["time"] <= 0:
                await setup_night(chat_id, chat["day"])

            await asyncio.sleep(5)
            return await countdown_mafia(chat_id=chat_id)
    except Exception as e:
        print("Countdown Mafia:" , e)

async def distribution_roles(chat_id):
    try:
        chat = GetDataFromChat.export_data_from_chat(chat=chat_id)

        for temp in chat["message"]:
            try:
                await bot.delete_message(chat_id=chat_id, message_id=temp["message_id"])

            except:
                pass
        
        dirs = os.listdir(os.getcwd() + "/data/chats/" + str(chat_id) + "/mafia")
        players = list(dirs)
        members = len(dirs)

        if members < 4:
            for temp in dirs:
                os.remove(os.getcwd() + "/data/chats/" + str(chat_id) + "/mafia/" + temp)

                profile = GetDataFromUser.get_data_user(int(temp.replace(".json", "")))
                profile["player_game"] = None
                GetDataFromUser.set_data_user(int(temp.replace(".json", "")), profile)

            GetDataFromChat.remove_game_from_chat(chat_id)
            return await bot.send_message(chat_id=chat_id, text=data["emojio"] + " *Мафия*\nНедостаточно игроков для начала игры..")
        
        mafia, police, medic, bomj = 0, 0, 0, 0

        if members == 4:

            mafia = 1

        elif members > 4 and members <= 6:

            mafia = 1
            medic = 1
            police = 1

        elif members > 6 and members <= 8:

            mafia = 2
            medic = 1
            police = 1
            bomj = 1

        else:

            mafia = 3
            medic = 1
            police = 1
            bomj = 1

        mafia_players, police_players, medic_players, bomj_players = [], [], [], []

        for _ in range(mafia + medic + police + bomj):
            if mafia > 0:

                mafia -= 1
                player = random.choice(players)
                players.remove(player)

                mafia_players.append(player)
                continue

            if police > 0:

                police -= 1
                player = random.choice(players)
                players.remove(player)

                police_players.append(player)
                continue

            if medic > 0:

                medic -= 1
                player = random.choice(players)
                players.remove(player)

                medic_players.append(player)
                continue

            if bomj > 0:

                bomj -= 1
                player = random.choice(players)
                players.remove(player)

                bomj_players.append(player)
                continue


        for temp in dirs:

            with open(os.getcwd() + "/data/chats/" + str(chat_id) + "/mafia/" + temp, encoding="UTF-8") as file:
                info = json.loads(file.read())

            if temp in mafia_players:

                data_mafia = {
                    "name": info["name"],
                    "role": "Mafia",
                    "alive": True,
                    "choise": None
                }
                with open("data/chats/" + str(chat_id) + "/mafia/" + temp, "+w", encoding="UTF-8") as file:
                    json.dump(data_mafia, file, ensure_ascii=False, indent=4)
                
                await bot.send_message(chat_id=int(temp.replace(".json", "")), text="🤵 Ваша роль: Мафия\nВы являетесь хозяином ночи, выбирайте кого убивать чтобы выиграть")
                continue

            if temp in police:

                data_mafia = {
                    "name": info["name"],
                    "role": "Police",
                    "alive": True,
                    "choise": None
                }
                with open("data/chats/" + str(chat_id) + "/mafia/" + temp, "+w", encoding="UTF-8") as file:
                    json.dump(data_mafia, file, ensure_ascii=False, indent=4)
                
                await bot.send_message(chat_id=int(temp.replace(".json", "")), text="👮 Ваша роль: Коммисар\nВы порядок и правосудие!\nПроверяйте игроков, чтобы выяснить кто убийца..")
                continue

            if temp in medic:

                data_mafia = {
                    "name": info["name"],
                    "role": "Medic",
                    "alive": True,
                    "choise": None
                }
                with open("data/chats/" + str(chat_id) + "/mafia/" + temp, "+w", encoding="UTF-8") as file:
                    json.dump(data_mafia, file, ensure_ascii=False, indent=4)
                
                await bot.send_message(chat_id=int(temp.replace(".json", "")), text="👨‍⚕️ Ваша роль: Врач\nЛечите людей, чтобы спасти их от смерти..")
                continue

            if temp in bomj_players:

                data_mafia = {
                    "name": info["name"],
                    "role": "Bomj",
                    "alive": True,
                    "choise": None
                }
                with open("data/chats/" + str(chat_id) + "/mafia/" + temp, "+w", encoding="UTF-8") as file:
                    json.dump(data_mafia, file, ensure_ascii=False, indent=4)
                
                await bot.send_message(chat_id=int(temp.replace(".json", "")), text="🧙‍♂️ Ваша роль: Бомж\nВам очень скучно по ночам\nХодите к игрокам дабы выпить с ними..")
                continue

            data_mafia = {
                    "name": info["name"],
                    "role": "Human",
                    "alive": True,
                    "choise": None
            }
            with open("data/chats/" + str(chat_id) + "/mafia/" + temp, "+w", encoding="UTF-8") as file:
                json.dump(data_mafia, file, ensure_ascii=False, indent=4)

            await bot.send_message(chat_id=int(temp.replace(".json", "")), text="🙎‍♂️ Ваша роль: Мирный")

        await bot.send_message(chat_id=chat_id, text=data["emojio"] + " *Мафия*\nИгра началась!")
        await setup_night(chat_id, 1)

    except Exception as e:
        print("Distribution Roles:" , e)

async def setup_night(chat_id, day):
    try:
        chat = GetDataFromChat.export_data_from_chat(chat=chat_id)

        chat["day"] = day
        chat["type"] = "Night"
        chat["time"] = 60

        GetDataFromChat.import_data_from_chat(chat_id, chat)

        dirs = os.listdir(os.getcwd() + "/data/chats/" + str(chat_id) + "/mafia")
        buttons = []

        for temp in dirs:

            with open(os.getcwd() + "/data/chats/" + str(chat_id) + "/mafia/" + temp, encoding="UTF-8") as file:
                info = json.loads(file.read())

            if info["role"] == "Human" or not info["alive"]:
                continue

            if info["role"] == "Mafia":
                message = "🤵 Кого убьём?"

            if info["role"] == "Police":
                message = "👮 Кого проверим?"

            if info["role"] == "Medic":
                message = "👨‍⚕️ Кого сегодня убьём?"

            if info["role"] == "Bomj":
                message = "🧙‍♂️ Кого сегодня убьём?"

            for item in dirs:

                with open(os.getcwd() + "/data/chats/" + str(chat_id) + "/mafia/" + item, encoding="UTF-8") as file:
                    mafia_info = json.loads(file.read())

                if (temp == item and info["role"] != "Medic") or not mafia_info["alive"]:
                    continue

                buttons.append(types.InlineKeyboardButton(text=mafia_info["name"], callback_data=f'{chat_id}_{int(item.replace(".json", ""))}_Night_{day}_{chat["hash"]}'))

            keyboard = types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(*buttons)

            await bot.send_message(chat_id=int(temp.replace(".json", "")), text=message, reply_markup=keyboard)

        image = open(os.getcwd() + "/games/night.jpg", "rb")
        await bot.send_photo(
        chat_id=chat_id, 
        photo=image, 
        caption=data["emojio"] + f' *Ночь, День #{day}*\n\n_Город расходится по домам, все ложаться спать\nПо городу начинаю бродить преступники и правохранители\nСладких вам снов.._', 
        parse_mode="Markdown")
            
    except Exception as e:
        print("Setup Night:" , e) 

async def setup_morning(chat_id, day):  
    try:
        chat = GetDataFromChat.export_data_from_chat(chat=chat_id)

        chat["day"] = day
        chat["type"] = "Morning"
        chat["time"] = 40

        GetDataFromChat.import_data_from_chat(chat_id, chat)
        dirs = os.listdir(os.getcwd() + "/data/chats/" + str(chat_id) + "/mafia")

        mafia_choise, police_choise, medic_choise, bomj_choise = [], [], [], []
        mafia_players, police_players, medic_players, bomj_players = [], [], [], []
        active_players = []

        for temp in dirs:
            with open(os.getcwd() + "/data/chats/" + str(chat_id) + "/mafia/" + temp, encoding="UTF-8") as file:
                user = json.loads(file.read())

            if not user["alive"] or user["choise"] is None:
                continue

            user_id = int(temp.replace(".json", ""))
            active_players.append(user_id)

            if user["role"] == "Mafia":
                mafia_choise.append(user["choise"])
                mafia_players.append(user_id)

            if user["role"] == "Police":
                police_choise.append(user["choise"])
                police_players.append(user_id)

            if user["role"] == "Medic":
                medic_choise.append(user["choise"])
                medic_players.append(user_id)
                

            if user["role"] == "Bomj":
                bomj_choise.append(user["choise"])
                bomj_players.append(user_id)

            user["choise"] = None
            with open(os.getcwd() + "/data/chats/" + str(chat_id) + "/mafia/" + temp, "+w", encoding="UTF-8") as file:
                json.dump(user, file, ensure_ascii=False, indent=4)

        for item in active_players:

            if item in bomj_choise:

                if item in mafia_players:
                    index = mafia_players.index(item)
                    mafia_choise.pop(index)

                if item in medic_players:
                    index = medic_players.index(item)
                    medic_choise.pop(index)

                if item in police_players:
                    index = police_players.index(item)
                    police_choise.pop(index)

        killed = None
        police = None
        medic = None

        if len(mafia_choise) != 0:
            killed = max(mafia_choise, key=mafia_choise.count) 

        if len(police_choise) != 0:   
            police = max(police_choise, key=police_choise.count)

        if len(medic_choise) != 0: 
            medic = max(medic_choise, key=medic_choise.count)

        message = data["emojio"] + f' *Утро, День #{day}*\n\n_Все жители города просыпаются\nИ начинают заниматься своими делами.._'

        if killed is not None:
            if medic is not None and killed == medic:
                return 

            with open(os.getcwd() + "/data/chats/" + str(chat_id) + "/mafia/" + str(killed) + ".json", encoding="UTF-8") as file:
                user = json.loads(file.read())

            user["alive"] = False

            with open(os.getcwd() + "/data/chats/" + str(chat_id) + "/mafia/" + str(killed) + ".json", "+w", encoding="UTF-8") as file:
                json.dump(user, file, ensure_ascii=False, indent=4)

            profile = GetDataFromUser.get_data_user(killed)
            profile["player_game"] = None
            GetDataFromUser.set_data_user(killed, profile)

            pin_user = f'[{user["name"]}](tg://user?id={killed})'
            message += f'\n\n⚰ К сожалению.. сегодня не стало {( user["name"] , pin_user )[ chat["pin_user"] ]}'

        if police is not None:
            with open(os.getcwd() + "/data/chats/" + str(chat_id) + "/mafia/" + str(police) + ".json", encoding="UTF-8") as file:
                user = json.loads(file.read())

            if user["role"] == "Mafia":
                pin_user = f'[{user["name"]}](tg://user?id={killed})'
                message += f'\n\n📺 Сегодня ночью *Коммисар* провёл расследование\nРезультат: {( user["name"] , pin_user )[ chat["pin_user"] ]} - Убийца'

            else:
                message += f'\n\n📺 Сегодня ночью *Коммисар* проводил расследование\nНе смог найти доказательств'

        image = open(os.getcwd() + "/games/morning.jpg", "rb")
        await bot.send_photo(
        chat_id=chat_id, 
        photo=image, 
        caption=message, 
        parse_mode="Markdown")

    except Exception as e:
        print("Setup Morning:" , e)

async def setup_day(chat_id, day):
    try:
        chat = GetDataFromChat.export_data_from_chat(chat=chat_id)

        chat["day"] = day
        chat["type"] = "Day"
        chat["time"] = 40

        GetDataFromChat.import_data_from_chat(chat_id, chat)
        dirs = os.listdir(os.getcwd() + "/data/chats/" + str(chat_id) + "/mafia")
        buttons = []

        for temp in dirs:
            for item in dirs:
                if temp == item:
                    continue

                with open(os.getcwd() + "/data/chats/" + str(chat_id) + "/mafia/" + item, encoding="UTF-8") as file:
                    mafia_info = json.loads(file.read())

                if not mafia_info["alive"]:
                    continue

                buttons.append(types.InlineKeyboardButton(text=mafia_info["name"], callback_data=f'{chat_id}_{int(item.replace(".json", ""))}_Day_{day}_{chat["hash"]}'))

            keyboard = types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(*buttons)

            await bot.send_message(chat_id=int(temp.replace(".json", "")), text=data["emojio"] + " За кого будем голосовать?", reply_markup=keyboard)

        await bot.send_message(chat_id=chat_id, text=data["emojio"] + " *Началось собрание жителей города*\n\n_На собрании вам нужно определиться, кого повесить за убийства в городе_", parse_mode="Markdown")
    except Exception as e:
        print("Setup Day:" , e)

async def count_votes(chat_id, day):
    try:
        chat = GetDataFromChat.export_data_from_chat(chat=chat_id)

        chat["day"] = day + 1
        chat["type"] = "Voted"
        chat["time"] = 10

        GetDataFromChat.import_data_from_chat(chat_id, chat)
        dirs = os.listdir(os.getcwd() + "/data/chats/" + str(chat_id) + "/mafia")
        voted = []
        for item in dirs:
            with open(os.getcwd() + "/data/chats/" + str(chat_id) + "/mafia/" + item, encoding="UTF-8") as file:
                user = json.loads(file.read())

            if not user["alive"] or not user["choise"]:
                continue

            voted.append(user["choise"])

        killed = None
        if len(voted) != 0:
            killed = max(voted, key=voted.count)

        message = data["emojio"] + " *Голосование было завершено*\n\n"
        if killed is not None:
            with open(os.getcwd() + "/data/chats/" + str(chat_id) + "/mafia/" + str(killed) + ".json", encoding="UTF-8") as file:
                info = json.loads(file.read())

            pin_user = f'[{info["name"]}](tg://user?id={killed})'
            message += f'_{( info["name"] , pin_user )[ chat["pin_user"] ]} был подвешен на висилице.._'

            info["alive"] = False

            with open(os.getcwd() + "/data/chats/" + str(chat_id) + "/mafia/" + str(killed) + ".json", "+w", encoding="UTF-8") as file:
                json.dump(info, file, ensure_ascii=False, indent=4)

            profile = GetDataFromUser.get_data_user(killed)
            profile["player_game"] = None
            GetDataFromUser.set_data_user(killed, profile)

        else:
            message += "_Жители не пришли к единому решению.._"

        await bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown")

    except Exception as e:
        print("Setup Voted:" , e)

async def checking_alive_user(chat_id):
    try:
        chat = GetDataFromChat.export_data_from_chat(chat=chat_id)
        if chat["action"] == "Mafia" and chat["type"] != "Register":

            mafia_count = 0
            human_count = 0

            dirs = os.listdir(os.getcwd() + "/data/chats/" + str(chat_id) + "/mafia")
            for temp in dirs:
                with open(os.getcwd() + "/data/chats/" + str(chat_id) + "/mafia/" + temp, encoding="UTF-8") as file:
                    user = json.loads(file.read())

                if user["role"] == "Mafia" and user["alive"]:
                    mafia_count += 1

                if user["alive"] and user["role"] != "Mafia":
                    human_count += 1

            if human_count <= 1:
                await end_mafia(chat_id)

            if mafia_count <= 0:
                await end_mafia(chat_id, True)
                
    except Exception as e:
        print("Setup Checking:" , e)

async def end_mafia(chat_id, human_win=False):
    try:
        chat = GetDataFromChat.export_data_from_chat(chat=chat_id)
        dirs = os.listdir(os.getcwd() + "/data/chats/" + str(chat_id) + "/mafia")

        message = data["emojio"] + " *Мафия\nИгра окончена*\n\nУчастники:\n"
        
        for temp in dirs:
            with open(os.getcwd() + "/data/chats/" + str(chat_id) + "/mafia/" + temp, encoding="UTF-8") as file:
                user = json.loads(file.read())

            os.remove(os.getcwd() + "/data/chats/" + str(chat_id) + "/mafia/" + temp)

            profile = GetDataFromUser.get_data_user(int(temp.replace(".json", "")))
            profile["player_game"] = None

            pin_user = f'[{user["name"]}](tg://user?id={int(temp.replace(".json", ""))})'

            if user["role"] == "Mafia":
                message += " 🤵 "
            
            elif user["role"] == "Police":
                message += " 👮 "

            elif user["role"] == "Medic":
                message += " 👨‍⚕️ "

            elif user["role"] == "Bomj":
                message += " 🧙 "

            elif user["role"] == "Human":
                message += " 🙎‍♂️ "

            message += f'{( user["name"] , pin_user )[ chat["pin_user"] ]}'
            if user["alive"]:

                message += f' +{data["winner_mafia"]} 💰'
                profile["player_game"] += data["winner_mafia"]
                GetDataFromUser.give_referal_money(user_id=profile["player_invited"], ammount=data["winner_mafia"])

            elif not user["alive"]:
                message += " (Мёртв)"

            message += "\n"
            GetDataFromUser.set_data_user(int(temp.replace(".json", "")), profile)

        if human_win:
            message += "\nПобедители - *Мирные жители*"
        
        if not human_win:
            message += "\nПобедители - *Мафия*"

        GetDataFromChat.remove_game_from_chat(chat_id)

        await bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown")
    except Exception as e:
        print("Setup Checking:" , e)

async def choise_user(from_id, message_id, chat_id, user_choise, value, day, hash):
    try:
        chat = GetDataFromChat.export_data_from_chat(chat=chat_id)

        if chat["day"] != day or chat["hash"] != hash or chat["type"] != value:
            return await bot.delete_message(chat_id=from_id, message_id=message_id)

        if not os.path.isfile(os.getcwd() + "/data/chats/" + str(chat_id) + "/mafia/" + str(from_id) + ".json"):
            return await bot.delete_message(chat_id=from_id, message_id=message_id)

        with open(os.getcwd() + "/data/chats/" + str(chat_id) + "/mafia/" + str(from_id) + ".json", encoding="UTF-8") as file:
            user = json.loads(file.read())

        #if user["role"] != "Mafia" and user["role"] != "Police" and user["role"] != "Medic" and user["role"] != "Bomj" or not user["alive"]:
            #return await bot.delete_message(chat_id=from_id, message_id=message)

        if not os.path.isfile(os.getcwd() + "/data/chats/" + str(chat_id) + "/mafia/" + str(user_choise) + ".json"):
            return 

        with open(os.getcwd() + "/data/chats/" + str(chat_id) + "/mafia/" + str(user_choise) + ".json", encoding="UTF-8") as file:
            info = json.loads(file.read())

        if not info["alive"]:
            return

        user["choise"] = user_choise
        with open(os.getcwd() + "/data/chats/" + str(chat_id) + "/mafia/" + str(from_id) + ".json", "+w", encoding="UTF-8") as file:
            json.dump(user, file, ensure_ascii=False, indent=4)

        message = None
        message_for_user = None

        if chat["type"] == "Night":

            if user["role"] == "Mafia":
                message = f'🤵 Вы выбрали [{info["name"]}](tg://user?id={user_choise})'
                message_for_user = "🤵 В качестве жертвы, выбрали вас..."

            if user["role"] == "Police":
                message = f'👮 Вы решили проверить [{info["name"]}](tg://user?id={user_choise})'
                message_for_user = "👮 Кто-то занялся вашим досье..."

            if user["role"] == "Medic":
                message = f'👨‍⚕️ Вы вылечили [{info["name"]}](tg://user?id={user_choise})'
                message_for_user = "👨‍⚕️ Врачи позаботились о вашем здоровье."

            if user["role"] == "Bomj":
                message = f'🧙 Вы выпили с [{info["name"]}](tg://user?id={user_choise})'
                message_for_user = "🧙 К вам пришёл Бомж, уделите ему пару рюмок."

            await bot.edit_message_text(text=message, chat_id=from_id, message_id=message_id)
            return await bot.send_message(chat_id=user_choise, text=message_for_user)

        message = f'🙎‍♂️ Вы проголосовали за [{info["name"]}](tg://user?id={user_choise})'
        return await bot.edit_message_text(text=message, chat_id=from_id, message_id=message_id)

    except Exception as e:
        print("choise_user:" , e)