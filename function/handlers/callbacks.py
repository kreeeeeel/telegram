import os
import json
import logging

from aiogram import types
from dispatcher import dp, bot

from function.games import mafia
from function.games import blackjack
from function.games import crocodile
from function.player import referal
from function.chat import settings
from function import admin
from classes import GetDataFromChat

config = open(os.getcwd() + "/config.json", encoding="UTF-8")
data = json.loads(config.read())
config.close()

@dp.callback_query_handler(lambda callback_query: True)
async def some_callback_handler(callback_query: types.CallbackQuery):
    try:
        code = callback_query.data
        if code == "Команды":
            
            caption = '*⚙ Настройка беседы:*\n'
            caption += "_/settings - Настройки_\n"
            caption += "\n*🔫 Игры для бесед:*\n"
            caption += "_/association - Игра Ассоциации_\n"
            caption += "_/blackjack - Игра Блэк-Джек_\n"
            caption += "_/crocodile - Игра Крокодил_\n"
            caption += "_/double - Игра Дабл_\n"
            caption += "_/mafia - Игра Мафия_\n"
            caption += "\n*📌 Остальные команды:*\n"
            caption += "_/profile - Личная статистика_\n"
            caption += "_/transfer - Перевод средств_\n"
            caption += "_/referal - Реферальная система_\n"
            caption += "_/startgame - Запуск игры_\n"

            return await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text=caption)

        elif code == "Проверить":
            if not await admin.is_admin_group(chat_id=callback_query.message.chat.id, user_id=bot.id):
                return 

            caption = data["emojio"] + " Отлично! Права были выданы\nМожем приступать к играм)"
            chat = GetDataFromChat.export_data_from_chat(chat=callback_query.message.chat.id)
            chat["working"] = True
            GetDataFromChat.import_data_from_chat(chat=callback_query.message.chat.id, data=chat)
            
            return await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text=caption)

        elif code == "Упоминание":
            if not callback_query.message.reply_to_message:
                return await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)

            if callback_query.from_user.id != callback_query.message.reply_to_message.from_user.id:
                return await bot.answer_callback_query(callback_query_id=callback_query.id, text=data["emojio"] + " Кнопка предназначана не для вас..", show_alert=True)

            if not await admin.is_admin_group(chat_id=callback_query.message.chat.id, user_id=callback_query.from_user.id):
                return await bot.answer_callback_query(callback_query_id=callback_query.id, text=data["emojio"] + " Недостаточно прав..", show_alert=True)

            if not await admin.is_admin_group(chat_id=callback_query.message.chat.id, user_id=bot.id):
                return await bot.answer_callback_query(callback_query_id=callback_query.id, text=data["emojio"] + " Недостаточно прав..", show_alert=True)

            chat = GetDataFromChat.export_data_from_chat(chat=callback_query.message.chat.id)
            if chat["pin_user"]:
                chat["pin_user"] = False
            else:
                chat["pin_user"] = True

            caption = data["emojio"] + f" Настройки беседы: {callback_query.message.chat.full_name}\n\n"
            caption += f'Упоминание: {( "Выключено ❌" , "Включено ✔" )[ chat["pin_user"] ]}'

            buttons  = [types.InlineKeyboardButton(text='Назад', callback_data="Настройки")] 
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(*buttons)

            GetDataFromChat.import_data_from_chat(chat=callback_query.message.chat.id, data=chat)
            return await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text=caption, reply_markup=keyboard)

        elif code == "Анти-КАПС":
            if not callback_query.message.reply_to_message:
                return await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)

            if callback_query.from_user.id != callback_query.message.reply_to_message.from_user.id:
                return await bot.answer_callback_query(callback_query_id=callback_query.id, text=data["emojio"] + " Кнопка предназначана не для вас..", show_alert=True)

            if not await admin.is_admin_group(chat_id=callback_query.message.chat.id, user_id=callback_query.from_user.id):
                return await bot.answer_callback_query(callback_query_id=callback_query.id, text=data["emojio"] + " Недостаточно прав..", show_alert=True)

            if not await admin.is_admin_group(chat_id=callback_query.message.chat.id, user_id=bot.id):
                return await bot.answer_callback_query(callback_query_id=callback_query.id, text=data["emojio"] + " Недостаточно прав..", show_alert=True)

            chat = GetDataFromChat.export_data_from_chat(chat=callback_query.message.chat.id)
            if chat["anti_capslock"]:
                chat["anti_capslock"] = False
            else:
                chat["anti_capslock"] = True

            caption = data["emojio"] + f" Настройки беседы: {callback_query.message.chat.full_name}\n\n"
            caption += f'Анти-КАПС: {( "Выключено ❌" , "Включено ✔" )[ chat["anti_capslock"] ]}'

            buttons  = [types.InlineKeyboardButton(text='Назад', callback_data="Настройки")] 
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(*buttons)
            GetDataFromChat.import_data_from_chat(chat=callback_query.message.chat.id, data=chat)
            return await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text=caption, reply_markup=keyboard)

        elif code == "Анти URL":
            if not callback_query.message.reply_to_message:
                return await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)

            if callback_query.from_user.id != callback_query.message.reply_to_message.from_user.id:
                return await bot.answer_callback_query(callback_query_id=callback_query.id, text=data["emojio"] + " Кнопка предназначана не для вас..", show_alert=True)

            if not await admin.is_admin_group(chat_id=callback_query.message.chat.id, user_id=callback_query.from_user.id):
                return await bot.answer_callback_query(callback_query_id=callback_query.id, text=data["emojio"] + " Недостаточно прав..", show_alert=True)

            if not await admin.is_admin_group(chat_id=callback_query.message.chat.id, user_id=bot.id):
                return await bot.answer_callback_query(callback_query_id=callback_query.id, text=data["emojio"] + " Недостаточно прав..", show_alert=True)

            chat = GetDataFromChat.export_data_from_chat(chat=callback_query.message.chat.id)
            if chat["anti_url"]:
                chat["anti_url"] = False
            else:
                chat["anti_url"] = True

            caption = data["emojio"] + f" Настройки беседы: {callback_query.message.chat.full_name}\n\n"
            caption += f'Анти URL: {( "Выключено ❌" , "Включено ✔" )[ chat["anti_url"] ]}'

            buttons  = [types.InlineKeyboardButton(text='Назад', callback_data="Настройки")] 
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(*buttons)
            GetDataFromChat.import_data_from_chat(chat=callback_query.message.chat.id, data=chat)
            return await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text=caption, reply_markup=keyboard)

        elif code == "Настройки":

            if not callback_query.message.reply_to_message:
                return await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)

            if callback_query.from_user.id != callback_query.message.reply_to_message.from_user.id:
                return await bot.answer_callback_query(callback_query_id=callback_query.id, text=data["emojio"] + " Кнопка предназначана не для вас..", show_alert=True)

            if not await admin.is_admin_group(chat_id=callback_query.message.chat.id, user_id=callback_query.from_user.id):
                return await bot.answer_callback_query(callback_query_id=callback_query.id, text=data["emojio"] + " Недостаточно прав..", show_alert=True)

            if not await admin.is_admin_group(chat_id=callback_query.message.chat.id, user_id=bot.id):
                return await bot.answer_callback_query(callback_query_id=callback_query.id, text=data["emojio"] + " Недостаточно прав..", show_alert=True)


            caption, keyboard = settings.get_settings(chat_id=callback_query.message.chat.id,full_name=callback_query.message.chat.full_name)

            return await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text=caption, reply_markup=keyboard)

        elif code == "Продолжить":
            return await crocodile.keyboard_wait(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, user_id=callback_query.from_user.id)

        elif code == "Рефералы":
            if not callback_query.message.reply_to_message:
                return await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)

            if callback_query.from_user.id != callback_query.message.reply_to_message.from_user.id:
                return await bot.answer_callback_query(callback_query_id=callback_query.id, text=data["emojio"] + " Кнопка предназначана не для вас..", show_alert=True)

            return await referal.get_user_referals(from_user=callback_query.from_user.id, chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
        
        elif code == "Ссылка":

            if not callback_query.message.reply_to_message:
                return await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)

            if callback_query.from_user.id != callback_query.message.reply_to_message.from_user.id:
                return await bot.answer_callback_query(callback_query_id=callback_query.id, text=data["emojio"] + " Кнопка предназначана не для вас..", show_alert=True)

            caption = data["emojio"] + f' *Реферальная система*\nВаша реферальная ссылка [тут](https://t.me/{data["name"]}?start={callback_query.from_user.id})'

            buttons = [types.InlineKeyboardButton(text='Рефералы', callback_data="Рефералы"), types.InlineKeyboardButton(text='Назад', callback_data="Назад")]
            keyboard = types.InlineKeyboardMarkup(row_width=2)
            keyboard.add(*buttons)

            return await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text=caption, reply_markup=keyboard)

        elif code == "Назад":

            if not callback_query.message.reply_to_message:
                return await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)

            if callback_query.from_user.id != callback_query.message.reply_to_message.from_user.id:
                return await bot.answer_callback_query(callback_query_id=callback_query.id, text=data["emojio"] + " Кнопка предназначана не для вас..", show_alert=True)

            caption, keyboard = referal.get_message_referal(callback_query.from_user.id)

            return await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text=caption, reply_markup=keyboard)

        code_splited = code.split("_")
        if code_splited[0] == "get" or code_splited[0] == "skip":
            action, chat_id, hashed = code_splited[0], code_splited[1], code_splited[2]
            return await blackjack.buttons_blackjack(
                from_id=callback_query.from_user.id, 
                message_id=callback_query.message.message_id, 
                action=action, 
                chat_id=chat_id, 
                hash=hashed
            )

        chat_id, user, value, day, hash = code.split("_")
        await mafia.choise_user(
            from_id=callback_query.from_user.id,
            message_id=callback_query.message.message_id, 
            chat_id=chat_id, 
            user_choise=int(user), 
            value=value, 
            day=int(day), 
            hash=int(hash)
        )
    except Exception as e:
        logging.error(e, exc_info=True)
