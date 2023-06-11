import asyncio
import os
from main import bot, dp
from db import db
from aiogram.types import Message, CallbackQuery
from keyboards import admin as nav
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import MessageNotModified
from contextlib import suppress
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import BotBlocked
from config import admin_id


class Post(StatesGroup):
    waiting_text = State()
    waiting_photo = State()


@dp.message_handler(commands=['admin'])
async def admin_panel(message: Message):
    if message.from_user.id == admin_id:
        await message.answer('Открыта админ панель.', reply_markup=nav.admin_keyboard)


@dp.message_handler(lambda message: message.text in ['Рассылка', 'Выгрузка БД', 'Статистика'])
async def process_news_command(message: Message, state: FSMContext):
    if message.from_user.id == admin_id:
        if message.text == 'Рассылка':
            await message.answer('Введите текст для рассылки 👇')
            await Post.waiting_text.set()
        elif message.text == 'Выгрузка БД':
            file_path = 'data.xlsx'
            db.export_users(file_path)
            with open(file_path, 'rb') as file:
                await bot.send_document(message.from_user.id, document=file, caption='Таблица users')

        elif message.text == 'Статистика':
            bot_statics = db.get_statistics()
            await message.answer(f'Статистика пользователей в боте: {bot_statics}')


@dp.message_handler(state=Post.waiting_text)
async def get_text_for_post(message: Message, state: FSMContext):
    async with state.proxy() as data:  # Устанавливаем состояние ожидания

        data['waiting_text'] = message.text
        await message.answer(f"Ваш пост:\n\n{data['waiting_text']}", reply_markup=nav.btn_mailing)
        await state.reset_state(with_data=False)


@dp.callback_query_handler(lambda call: call.data in ['add_picture', 'mail_confirm', 'mail_cancel'])
async def standart_mailing_settings(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        message_text = data['waiting_text']

        with suppress(MessageNotModified):
            if call.data == 'add_picture':
                await call.message.edit_text('📲Прекрепите картинку')
                await Post.waiting_photo.set()

            if call.data == 'mail_confirm':
                await bot.answer_callback_query(call.id)
                await call.message.delete()

                user_ids, count_before = db.mailing()
                count_after = 0
                for user_id in user_ids:
                    try:
                        await bot.send_message(user_id[0], message_text)
                        count_after += 1
                    except BotBlocked:
                        pass

                    await asyncio.sleep(5)

                await call.message.answer(
                    f'Сообщение было успешно отправлено: {str(count_after)} из {str(count_before)} пользователей')

            elif call.data == 'mail_cancel':
                await call.message.edit_text('Рассылка отменена!')


@dp.message_handler(state=Post.waiting_photo, content_types=types.ContentType.PHOTO)  # Принимаем состояние
async def set_mailing_photo(message: Message, state: FSMContext):
    async with state.proxy() as data:  # Устанавливаем состояние ожидания
        data['waiting_photo'] = message.photo[-1].file_id
        await bot.send_photo(message.chat.id, photo=data['waiting_photo'], caption=data['waiting_text'],
                             reply_markup=nav.btn_photo_mailing)
        await state.reset_state(with_data=False)


@dp.callback_query_handler(lambda call: call.data in ['photo_confirm', 'photo_cancel'])
async def send_mailing_photo(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        message_text = data['waiting_text']
        message_photo = data['waiting_photo']
        with suppress(MessageNotModified):
            user_ids, count_before = db.mailing()
            count_after = 0
            if call.data == 'photo_confirm':
                await call.message.delete()
                for user_id in user_ids:
                    try:
                        await bot.send_photo(user_id[0], photo=message_photo, caption=message_text)
                        count_after += 1
                    except BotBlocked:
                        pass

                    await asyncio.sleep(5)

                await call.message.answer(
                    f'Сообщение было успешно отправлено: {str(count_after)} из {str(count_before)} пользователей')

            elif call.data == 'photo_cancel':
                await call.message.delete()
                await call.message.answer('Рассылка отменена!')

            await state.finish()