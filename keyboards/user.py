from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from translations import _


def main_menu(lang):
    # main menu
    item_1 = KeyboardButton(_('📥Шифрование', lang))
    item_2 = KeyboardButton(_('📤Расшифрование', lang))
    item_3 = KeyboardButton(_('📚Инструкции', lang))
    item_4 = KeyboardButton(_('⚙Настройки', lang))
    item_5 = KeyboardButton(_('☎Поддержка', lang))

    markup = ReplyKeyboardMarkup(
        resize_keyboard=True,
        input_field_placeholder="Выберите команду")

    markup.row(item_1, item_2)
    markup.row(item_3, item_4)
    markup.add(item_5)

    return markup


def lang_menu(lang):
    lang_ru = InlineKeyboardButton(_('🇷🇺Русский', lang), callback_data='lang_ru')
    lang_en = InlineKeyboardButton(_('🇬🇧Английский', lang), callback_data='lang_en')

    language = InlineKeyboardMarkup(row_width=2)
    language.add(lang_ru, lang_en)

    return language


# encrypt methods
aes = InlineKeyboardButton('aes', callback_data='set_aes')
blowfish = InlineKeyboardButton('blowfish', callback_data='set_blowfish')
# rc4 = InlineKeyboardButton('rc4', callback_data='set_rc4')
sha256 = InlineKeyboardButton('sha256', callback_data='set_sha256')
# xor = InlineKeyboardButton('xor', callback_data='set_xor')


btn_method = InlineKeyboardMarkup(row_width=1)
btn_method.add(aes, blowfish, sha256)


# decrypt methods
aes = InlineKeyboardButton('aes', callback_data='decrypt_aes')
blowfish = InlineKeyboardButton('blowfish', callback_data='decrypt_blowfish')
# rc4 = InlineKeyboardButton('rc4', callback_data='decrypt_rc4')
sha256 = InlineKeyboardButton('sha256', callback_data='decrypt_sha256')
# xor = InlineKeyboardButton('xor', callback_data='decrypt_xor')

btn_decrypt = InlineKeyboardMarkup(row_width=1)
btn_decrypt.add(aes, blowfish, sha256)


def cancel_action(lang):
    # cancel button
    cancel = InlineKeyboardButton(_('❌Отмена', lang), callback_data='set_cancel')
    btn_cancel = InlineKeyboardMarkup(row_width=1)
    btn_cancel.add(cancel)

    return btn_cancel