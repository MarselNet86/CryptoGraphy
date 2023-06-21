import asyncio
import os
from main import bot, dp
from db import db
from aiogram.types import Message, CallbackQuery
from keyboards import user as nav
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import MessageNotModified
from contextlib import suppress
from aiogram import types
from aiogram.dispatcher import FSMContext
from methods.sha256 import decrypt_sha256
from methods.aes_ctr import decrypt_file_aes_ctr
from methods.blowfish import decrypt_file_blowfish
from translations import _


class Post(StatesGroup):
    waiting_for_document = State()
    waiting_for_key = State()


@dp.callback_query_handler(lambda call: 'decrypt' in call.data)
async def get_file_decrypt(call: CallbackQuery, state: FSMContext):
    with suppress(MessageNotModified):
        lang = db.get_lang(call.message.chat.id)
        method_name = call.data.split('_')[1]

        if lang == 'ru':
            send_message = await call.message.edit_text(f'Выбран: {method_name}'
                                                    '\n\nОтправьте мне свой файл: ', reply_markup=nav.cancel_action(lang))
        else:
            send_message = await call.message.edit_text(f'Selected: {method_name}'
                                                    '\n\nSend me your file: ', reply_markup=nav.cancel_action(lang))

        await state.update_data(method=method_name, send_message=send_message)  # Сохраняем значение в состоянии
        await Post.waiting_for_document.set()


@dp.message_handler(content_types=types.ContentTypes.DOCUMENT, state=Post.waiting_for_document)
async def get_key_decrypt(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        lang = db.get_lang(message.from_user.id)
        document = message.document
        file_path = f"downloads/{document.file_name}"
        send_message = data.get('send_message')  # Получаем значение из состояния
        await Post.waiting_for_key.set()

        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        await bot.edit_message_text(chat_id=message.from_user.id, message_id=send_message.message_id,
                                    text=_('🔑Введите ключ расшифрования:', lang))

        # Загрузка файла и сохранение в папку /downloads
        await bot.download_file_by_id(document.file_id, file_path)
        await state.update_data(file_path=file_path)


@dp.message_handler(state=Post.waiting_for_key)
async def decrypt_master(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        lang = db.get_lang(message.from_user.id)
        file_path = data['file_path']
        key = message.text

        data = await state.get_data()
        method_name = data.get('method')
        try:
            if method_name == 'aes':
                output_file = decrypt_file_aes_ctr(file_path, key)

            elif method_name == 'sha256':
                output_file = decrypt_sha256(file_path, key)

            elif method_name == 'blowfish':
                output_file = decrypt_file_blowfish(file_path, key)

            # функции в режиме апробации
            """
            elif method_name == 'rc4':
                output_file = decrypt_rc4(file_path, key)

            elif method_name == 'xor':
                output_file = decrypt_file_xor(file_path, int(key))
            """

            if lang == 'ru':
                key_answer = (f'📮Метод расшифрования: {method_name}\n\n'
                            '⚠Сообщение с файлом будет удалено через 1 минуту!')
            else:
                key_answer = (f'📮Decryption method: {method_name}\n\n'
                            '⚠Message with file will be deleted in 1 minute!')

            with open(output_file, 'rb') as file:
                send_message = await bot.send_document(message.from_user.id, document=file, caption=key_answer)
            os.remove(output_file)

            db.post_dec_statics(message.from_user.id)

        except Exception as e:
            print(e)
            await message.answer(_(f'🚫Ошибка при расшифровке файла!\n\n❗Ваш файл поврежден или имеет не верный ключ расшифровки!', lang))

        await state.finish()
        await asyncio.sleep(60)
        await send_message.delete()


@dp.callback_query_handler(text='set_cancel', state=Post.waiting_for_document)
async def go_back(call: CallbackQuery, state: FSMContext):
    await state.finish()
    lang = db.get_lang(call.message.chat.id)
    await call.message.edit_text(_('🔙Действие отменено', lang))