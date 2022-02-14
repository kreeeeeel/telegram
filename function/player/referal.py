import json
import os
import logging

from aiogram import types
from dispatcher import dp, bot

from classes import GetDataFromUser, GetDataFromChat

config = open(os.getcwd() + "/config.json", encoding="UTF-8")
data = json.loads(config.read())
config.close()

@dp.message_handler(commands=['referal'])
async def referal_handler(message: types.Message):
    try:
        if message.chat.id != message.from_user.id:
            chat = GetDataFromChat.export_data_from_chat(chat=message.chat.id)
            if chat["working"] is False:
                return

        if not GetDataFromUser.is_user_data(user_id=message.from_user.id):
            return await message.answer(text=data["emojio"] + " *Реферальная система*\nЧтобы пользоваться вам нужно начать диалог с ботом\nИли же перейти по ссылке от своего друга.")

        value = message.get_args()

        if value:
            splited = value.split(" ")
            if len(splited) != 0:

                if splited[0].lower() != "снять" or len(splited) == 2 and splited[1] and not splited[1].isdigit():
                    return await message.reply(text=data["emojio"] + " Чтобы снять реферальные деньги\nИспользуйте: */referal снять <кол-во>*\n_Если ко-во не указано, вычтеться весь баланс_")
            
                user = GetDataFromUser.get_data_user(user_id=message.from_user.id)
                if user["player_referal_balance"] <= 0:
                    return await message.reply(text=data["emojio"] + " *У вас нет реферальных средств..*")

                money = user["player_referal_balance"]
                if splited[1] and splited[1].isdigit():
                    money = int(splited[1])
                    if money > user["player_referal_balance"]:
                        return await message.reply(text=data["emojio"] + " *У вас недостаточно реферальных средств..*")

                if data["minimal_take_referal"] > money:
                    return await message.reply(text=data["emojio"] + f' Минимальная сумма снятия *{data["minimal_take_referal"]:,d} $*..')

                user["player_referal_balance"] -= money
                user["player_balance"] += money

                GetDataFromUser.set_data_user(user_id=message.from_user.id, data=user)
                return await message.reply(text=data["emojio"] + f' Вы сняли со счёта *{money:,d} $*\n💸 Ваш баланс: *{user["player_balance"]:,d} $*')

        caption, keyboard = get_message_referal(message.from_user.id)

        await message.reply(text=caption, reply_markup=keyboard, parse_mode="Markdown")
    except Exception as e:
        logging.error(e, exc_info=True)

def get_message_referal(user):
    data_user = GetDataFromUser.get_data_user(user_id=user)

    caption = data["emojio"] + f' *Реферальная система\n💰 Уровень: {data_user["player_referal_lvl"]}/{data["maximum_level_referal"]}*\n\n'
    caption += f'❓ Что такое Реферальная система\n❗ Реферальная система служит помощи игрокам\n  При приглашение своего друга по ссылке\n  Вы будете получать процент от ставок своего друга\n\n'
    caption += f'❓ Как пригласить своего друга?\n❗ Пригласить своего друга можно по ссылке\n  После чего ваш друг перейдя по ссылке\n  Нажать на кнопку *CТАРТ*\n\n'
    caption += f'❓ Бонусы\n❗ При приглашении вашего друга, он сможет получить бонус\n  В зависимости от уровня вашей реферальной системы\n\n'
        #caption += f'Ваша ссылка: https://t.me/{data["name"]}?start={from_user}'

    buttons = [types.InlineKeyboardButton(text='Мои рефералы', callback_data="Рефералы"), types.InlineKeyboardButton(text='Ссылка', callback_data="Ссылка")]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return (caption, keyboard)

async def get_user_referals(from_user, chat_id, message_id):

    data_user = GetDataFromUser.get_data_user(user_id=from_user)
    caption = data["emojio"] + " *Реферальная система*\n"

    if data_user["player_invited"] is not None:
        user = await bot.get_chat(chat_id=data_user["player_invited"])
        caption += f'Вас пригласил: [{user.full_name}](tg://user?id={data_user["player_invited"]})\n'
        
    if data_user["player_referals"]:
        caption += "*\nВы пригласили:*\n"
        count = len(data_user["player_referals"])
        for temp in data_user["player_referals"]:
            user_id = temp["user"]
            
            invited = await bot.get_chat(chat_id=user_id)
            caption += f'[{invited.full_name}](tg://user?id={user_id})\n'

        caption += f'\nВсего *{count}* чел.'

    else:
        caption += "\nВы никого не пригласили"

    buttons = [types.InlineKeyboardButton(text='Ссылка', callback_data="Ссылка"), types.InlineKeyboardButton(text='Назад', callback_data="Назад")]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)

    await bot.edit_message_text(chat_id=chat_id, text=caption, message_id=message_id, reply_markup=keyboard)
