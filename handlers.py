from main import bot, dp
from db import db
from aiogram.types import Message, CallbackQuery
from keyboards import user as nav
from translations import _
import decrypter
import encrypter
import admin_panel

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
        db.add_user(call.from_user.id, lang)
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
        await message.answer(_('Если у вас возникают вопросы по контенту EnDeFast, то вы можете задать их нашему менеджеру — @eXXPate 👨‍💻'
                               '\n\nМенеджер всегда поможет разобраться и ответит на любые интересующие вопросы по шифрованию/расшифрованию, а также поможет решить ваши проблемы 😉', lang))

    else:
        await message.answer(_('⚠Неизвестный метод, возвращаю в главное меню!', lang), reply_markup=nav.main_menu(lang))