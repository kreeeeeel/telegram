import os
import json

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

        # Created data
        data = {
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

class GetDataFromUser:

    def is_user_data(user_id):
        if os.path.isfile("data/users/" + str(user_id) + ".json"):
            return True

        return False

    def create_user_data(user_id, referal=None, Money=0):
        config = open(os.getcwd() + "/config.json", encoding="UTF-8")
        cfg = json.loads(config.read())
        config.close()

        dirs = os.listdir(os.getcwd() + "/data/users")
        # Created data
        data = {

            "player_uid": 10000+len(dirs),
            "player_level": 1,
            "player_exp": 0,
            "player_vip": False,
            "player_premium": False,
            "player_admin": True,
            "player_balance": cfg["start_money"]+Money,
            "player_shield_mafia": 0,
            "player_fake_docs": 0,
            "player_game": None,
            "player_referal_balance": 0,
            "player_referal_lvl": 1,
            "player_invited": referal,
            "player_referals": None
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
