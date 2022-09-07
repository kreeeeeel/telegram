from aiogram import executor
from dispatcher import dp
import function
import os

if __name__ == "__main__":
    if not os.path.isdir("data"):
        os.mkdir("data")
        
    if not os.path.isdir("data/chats"):
        os.mkdir("data/chats")
        
    executor.start_polling(dp, skip_updates=True)
