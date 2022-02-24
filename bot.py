from aiogram import Bot, Dispatcher, executor
import asyncio
from datetime import datetime
from datetime import timezone
from pytz import timezone

neketa = 237408360
bot = Bot(token="1947165848:AAF5FJxUmxPJNDa4KJxkFdIol-Q-SUI_TGo")
dp = Dispatcher(bot)

async def on_startup(_):
    date = datetime.now(timezone('Europe/Moscow'))
    if date.hour == 9 and date.minute == 30:
        await bot.send_message(chat_id=neketa, text='Кирюша пидор')

    await asyncio.sleep(30)
    await on_startup(_)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False, on_startup=on_startup)
