import logging
import os
import json

from aiogram import Bot, Dispatcher

config = open(os.getcwd() + "/config.json", encoding="UTF-8")
data = json.loads(config.read())
config.close()

# Logging
logging.basicConfig(level=logging.DEBUG)

# Dispatcher
bot = Bot(token=data["token"], parse_mode="Markdown")
dp = Dispatcher(bot)
