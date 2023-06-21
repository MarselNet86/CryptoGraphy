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
from methods.sha256 import encrypt_sha256
from methods.aes_ctr import encrypt_file_aes_ctr
from methods.blowfish import encrypt_file_blowfish
from translations import _


class Post(StatesGroup):
    encrypt_file = State()


@dp.callback_query_handler(lambda call: 'set' in call.data)
async def get_file_encrypt(call: CallbackQuery, state: FSMContext):
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
        await Post.encrypt_file.set()


@dp.message_handler(content_types=types.ContentTypes.DOCUMENT, state=Post.encrypt_file)
async def encrypt_master(message: types.Message, state: FSMContext):
    key = message.text
    lang = db.get_lang(message.from_user.id)

    data = await state.get_data()
    method_name = data.get('method')  # Получаем значение из состояния
    send_message = data.get('send_message')  # Получаем значение из состояния
    await bot.edit_message_text(chat_id=message.from_user.id, message_id=send_message.message_id, text=_('📂Зашифровываем данные...\n\n⏳Пожалуйста, подождите!', lang))

    document = message.document

    # Сохраняем файл на сервере
    file_path = f"downloads/{document.file_name}"
    await message.delete()
    await bot.download_file_by_id(document.file_id, file_path)

    if method_name == 'aes':
        key = encrypt_file_aes_ctr(document.file_name)

    elif method_name == 'sha256':
        key = encrypt_sha256(document.file_name)

    elif method_name == 'blowfish':
        key = encrypt_file_blowfish(document.file_name)

    # функции в режиме апробации
    """
    elif method_name == 'rc4':
        key = encrypt_rc4(document.file_name)

    elif method_name == 'xor':
        key = encrypt_file_xor(document.file_name)
    """

    os.remove(file_path)

    await bot.edit_message_text(chat_id=message.from_user.id, message_id=send_message.message_id, text=_('✅Файл успешно зашифрован!', lang))

    if lang == 'ru':
        key_answer = (f'📮Метод шифрования: {method_name}\n\n'
                    f'🔑Ваш ключ расшифрования файла: <code>{key}</code>\n\n'
                    '⚠Сообщение с файлом будет удалено через 1 минуту!')
    else:
        key_answer = (f'📮Encryption method: {method_name}\n\n',
                    f'🔑Your decryption key for the file: <code>{key}</code>\n\n'
                    f'⚠Message with file will be deleted in 1 minute!')

    output_file = os.path.splitext(file_path)[0] + '_enc' + os.path.splitext(file_path)[1]
    with open(output_file, 'rb') as file:
        send_message = await bot.send_document(message.from_user.id, document=file, caption=key_answer, parse_mode='HTML')
    os.remove(output_file)

    db.post_enc_statics(message.from_user.id)

    await state.finish()
    await asyncio.sleep(60)
    await send_message.delete()


@dp.callback_query_handler(text='set_cancel', state=Post.encrypt_file)
async def go_back(call: CallbackQuery, state: FSMContext):
    await state.finish()
    lang = db.get_lang(call.message.chat.id)
    await call.message.edit_text(_('🔙Действие отменено', lang))