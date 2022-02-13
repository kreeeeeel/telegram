import os
import json
from datetime import datetime
import pytz

tz = pytz.timezone('Europe/Moscow')

class GetDataFromChat:
    def is_created_chat(chat):

        if os.path.isdir("data/chats/" + str(chat)) and os.path.isfile("data/chats/" + str(chat) + "/settings.json"):
            return True

        return False

    def created_data_chat(chat):

        if not os.path.isdir("data/chats/" + str(chat)):
            os.mkdir("data/chats/" + str(chat))

        if not os.path.isdir("data/chats/" + str(chat) + "/mafia"):
            os.mkdir("data/chats/" + str(chat) + "/mafia")

        if not os.path.isdir("data/chats/" + str(chat) + "/blackjack"):
            os.mkdir("data/chats/" + str(chat) + "/blackjack")

        if not os.path.isdir("data/chats/" + str(chat) + "/double"):
            os.mkdir("data/chats/" + str(chat) + "/double")

        if not os.path.isdir("data/chats/" + str(chat) + "/double/x2"):
            os.mkdir("data/chats/" + str(chat) + "/double/x2")

        if not os.path.isdir("data/chats/" + str(chat) + "/double/x3"):
            os.mkdir("data/chats/" + str(chat) + "/double/x3")

        if not os.path.isdir("data/chats/" + str(chat) + "/double/x5"):
            os.mkdir("data/chats/" + str(chat) + "/double/x5")

        if not os.path.isdir("data/chats/" + str(chat) + "/double/x50"):
            os.mkdir("data/chats/" + str(chat) + "/double/x50")

        if not os.path.isdir("data/chats/" + str(chat) + "/association"):
            os.mkdir("data/chats/" + str(chat) + "/association")

        if not os.path.isdir("data/chats/" + str(chat) + "/crocodile"):
            os.mkdir("data/chats/" + str(chat) + "/crocodile")

        # Created data
        data = {
            "working": False,
            "pin_user": True,
            "anti_capslock": False,
            "anti_url": False,
            "action": None,
            "bet": None,
            "hash": None,
            "value": None,
            "type": None,
            "queue": None,
            "day": None,
            "message": None,
            "time": None
        }
        with open("data/chats/" + str(chat) + "/settings.json", "+w", encoding="UTF-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def import_data_from_chat(chat, data):
        with open("data/chats/" + str(chat) + "/settings.json", "+w", encoding="UTF-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def export_data_from_chat(chat):
        with open("data/chats/" + str(chat) + "/settings.json", encoding="UTF-8") as file:
            data = json.loads(file.read())
            file.close()

        return data

    def remove_game_from_chat(chat):
        with open("data/chats/" + str(chat) + "/settings.json", encoding="UTF-8") as file:
            data = json.loads(file.read())

        data["action"] = None
        data["bet"] = None
        data["value"] = None
        data["type"] = None
        data["message"] = None
        data["hash"] = None
        data["time"] = None
        data["queue"] = None

        with open("data/chats/" + str(chat) + "/settings.json", "+w", encoding="UTF-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def remove_bot_chat(chat_id):
        with open("data/chats/" + str(chat_id) + "/settings.json", encoding="UTF-8") as file:
            chat = json.loads(file.read())

        chat["working"] = False
        chat["action"] = None
        chat["bet"] = None
        chat["value"] = None
        chat["type"] = None
        chat["message"] = None
        chat["hash"] = None
        chat["time"] = None
        chat["queue"] = None

        with open("data/chats/" + str(chat_id) + "/settings.json", "+w", encoding="UTF-8") as file:
            json.dump(chat, file, ensure_ascii=False, indent=4)

        dirs = os.listdir(os.getcwd() + "/data/chats/" + str(chat_id) + "/association")
        for temp in dirs:
            os.remove(os.getcwd() + "/data/chats/" + str(chat_id) + "/association/" + temp)

        dirs = os.listdir(os.getcwd() + "/data/chats/" + str(chat_id) + "/blackjack")
        for temp in dirs:
            os.remove(os.getcwd() + "/data/chats/" + str(chat_id) + "/blackjack/" + temp)

            profile = GetDataFromUser.get_data_user(int(temp.replace(".json", "")))
            profile["player_game"] = None
            profile["player_balance"] += chat["bet"]
            GetDataFromUser.set_data_user(int(temp.replace(".json", "")), profile)

        dirs = os.listdir(os.getcwd() + "/data/chats/" + str(chat_id) + "/crocodile")
        for temp in dirs:
            os.remove(os.getcwd() + "/data/chats/" + str(chat_id) + "/crocodile/" + temp)

            profile = GetDataFromUser.get_data_user(int(temp.replace(".json", "")))
            profile["player_game"] = None
            GetDataFromUser.set_data_user(int(temp.replace(".json", "")), profile)
        
        positons = [2, 3, 5, 50]

        for item in positons:
            dirs = os.listdir(os.getcwd() + "/data/chats/" + str(chat_id) + "/double/x" + str(item))
            for temp in dirs:
                with open(os.getcwd() + "/data/chats/" + str(chat_id) + "/double/x" + str(item) + "/" + temp, encoding="UTF-8") as file:
                    user = json.loads(file.read())

                os.remove(os.getcwd() + "/data/chats/" + str(chat_id) + "/double/x" + str(item) + "/" + temp)

                user_id = int(temp.replace(".json", ""))
                data_user = GetDataFromUser.get_data_user(user_id)
                data_user["player_balance"] += user["bet"] * item

                GetDataFromUser.set_data_user(user_id, data_user)

        dirs = os.listdir(os.getcwd() + "/data/chats/" + str(chat_id) + "/mafia")

        for temp in dirs:
            os.remove(os.getcwd() + "/data/chats/" + str(chat_id) + "/mafia/" + temp)

            profile = GetDataFromUser.get_data_user(int(temp.replace(".json", "")))
            profile["player_game"] = None
            GetDataFromUser.set_data_user(int(temp.replace(".json", "")), profile)



class GetDataFromUser:

    def is_user_data(user_id):
        if os.path.isfile("data/users/" + str(user_id) + ".json"):
            return True

        return False

    def create_user_data(user_id, referal=None, Money=0):
        config = open(os.getcwd() + "/config.json", encoding="UTF-8")
        cfg = json.loads(config.read())
        config.close()

        time = datetime.now(tz)

        dirs = os.listdir(os.getcwd() + "/data/users")
        # Created data
        data = {
            
            "player_uid": 10000+len(dirs),
            "player_admin": True,
            "player_balance": cfg["start_money"]+Money,
            "player_game": None,
            "player_referal_balance": 0,
            "player_referal_lvl": 1,
            "player_invited": referal,
            "player_referals": None,
            "player_register_day": time.day,
            "player_register_month": time.month,
            "player_register_year": time.year,
            "player_register_hour": time.hour,
            "player_register_minute": time.minute
        }
        with open("data/users/" + str(user_id) + ".json", "+w", encoding="UTF-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def get_data_user(user_id):
        with open("data/users/" + str(user_id) + ".json", encoding="UTF-8") as file:
            data = json.loads(file.read())
            file.close()

        return data

    def set_data_user(user_id, data):
        with open("data/users/" + str(user_id) + ".json", "+w", encoding="UTF-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def give_referal_money(user_id, ammount):
        if not GetDataFromUser.is_user_data(user_id=user_id):
            return

        with open("data/users/" + str(user_id) + ".json", encoding="UTF-8") as file:
            data = json.loads(file.read())
        
        value = int(ammount * data["player_referal_lvl"] / 100)
        data["player_referal_balance"] += value

        with open("data/users/" + str(user_id) + ".json", "+w", encoding="UTF-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
