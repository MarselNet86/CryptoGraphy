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
from aiogram.utils.exceptions import BotBlocked
from methods.rc4 import encrypt_rc4, decrypt_rc4
from methods.sha256 import encrypt_sha256, decrypt_sha256
from methods.aes_ctr import encrypt_file_aes_ctr, decrypt_file_aes_ctr
from methods.blowfish import encrypt_file_blowfish, decrypt_file_blowfish
from methods.xor import encrypt_file_xor, decrypt_file_xor
from translations import _
import admin_panel


class Post(StatesGroup):
    encrypt_file = State()
    waiting_for_document = State()
    waiting_for_key = State()


@dp.message_handler(commands=['start'])
async def start(message: Message):
    if not db.user_exists(message.from_user.id):
        await message.answer('Выберите язык:', reply_markup=nav.lang_menu('ru'))
    else:
        lang = db.get_lang(message.from_user.id)
        await message.answer(_('Добро пожаловать!', lang), reply_markup=nav.main_menu(lang))


@dp.callback_query_handler(text_contains='lang_')
async def set_language(call: CallbackQuery):
    await bot.delete_message(call.from_user.id, call.message.message_id)
    lang = call.data[5:]
    if not db.user_exists(call.from_user.id):
        await db.add_user(call.from_user.id, lang)
        await call.message.answer(_('Успешная регистрация!', lang), reply_markup=nav.main_menu(lang))
    else:
        user_lang = db.get_lang(call.message.chat.id)
        if user_lang != lang:
            db.update_lang(lang, call.from_user.id)
            await call.message.answer(_('Настройки приняты!', lang), reply_markup=nav.main_menu(lang))
        else:
            await call.message.answer(_('🚩Нельзя ставить тот же регион!', lang), reply_markup=nav.main_menu(lang))


@dp.message_handler(content_types=['text'])
async def handle_buttons(message: Message):
    lang = db.get_lang(message.from_user.id)
    if message.text == _('📥Шифрование', lang):
        await message.answer(_('Выберите тип шифрования\n\nМетоды:', lang), reply_markup=nav.btn_method)

    elif message.text == _('📤Расшифрование', lang):
        await message.answer(_('Выберите тип расшифровки\n\nМетоды', lang), reply_markup=nav.btn_decrypt)

    elif message.text == _('📚Инструкции', lang):
        await message.answer(_('Содержание <a href="https://teletype.in/">руководство пользователя</a>:'
                               '\n\n● Первый запуск, знакомство с интерфейсом и методами шифрования'
                               '\n● Навигация по методам расшифрования'
                               '\n● Комьюнити-чат, обратная связь'
                               '\n● Сотрудничество, реклама'
                               '\n● FAQ', lang), parse_mode='HTML')

    elif message.text == _('⚙Настройки', lang):
        await message.answer(_('Выберите язык:', lang), reply_markup=nav.lang_menu(lang))

    elif message.text == _('☎Поддержка', lang):
        await message.answer(_('Если у вас возникают вопросы по контенту EnDeFast, то вы можете задать их нашему менеджеру — @PavelAstapenko 👨‍💻'
                               '\n\nМенеджер всегда поможет разобраться и ответит на любые интересующие вопросы по шифрованию/расшифрованию, а также поможет решить ваши проблемы 😉', lang))

    else:
        await message.answer(_('⚠Неизвестный метод, возвращаю в главное меню!', lang), reply_markup=nav.main_menu(lang))


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


@dp.callback_query_handler(text='set_cancel', state=Post.encrypt_file)
async def go_back(call: CallbackQuery, state: FSMContext):
    await state.finish()
    lang = db.get_lang(call.message.chat.id)
    await call.message.edit_text(_('🔙Действие отменено', lang))


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
                    f'🔑Ваш ключ расшифрования файла: {key}\n\n'
                    '⚠Сообщение с файлом будет удалено через 1 минуту!')
    else:
        key_answer = (f'📮Encryption method: {method_name}\n\n'
                    f'🔑Your decryption key for the file: {key}\n\n'
                    '⚠Message with file will be deleted in 1 minute!')

    # Отправляем файл обратно пользователю
    with open(file_path + '.enc', 'rb') as file:
        send_message = await bot.send_document(message.from_user.id, document=file, caption=key_answer)
    os.remove(file_path + '.enc')

    await state.finish()
    await asyncio.sleep(60)
    await send_message.delete()


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

        except:
            await message.answer(_(f'🚫Ошибка при расшифровке файла!\n\n❗Ваш файл поврежден или имеет не верный ключ расшифровки!', lang))

        await state.finish()
        await asyncio.sleep(60)
        await send_message.delete()


@dp.callback_query_handler(text='set_cancel', state=Post.waiting_for_document)
async def go_back(call: CallbackQuery, state: FSMContext):
    await state.finish()
    lang = db.get_lang(call.message.chat.id)
    await call.message.edit_text(_('🔙Действие отменено', lang))



