from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

item_1 = KeyboardButton('Рассылка')
item_2 = KeyboardButton('Выгрузка БД')
item_3 = KeyboardButton('Статистика')
admin_keyboard = ReplyKeyboardMarkup(
    resize_keyboard=True,
    input_field_placeholder="Выберите команду")

admin_keyboard.add(item_1, item_2)
admin_keyboard.row(item_3)


picture = InlineKeyboardButton('🌄Добавить картинку', callback_data='add_picture')
confirm = InlineKeyboardButton('✅Подтвердить', callback_data='mail_confirm')
cancel = InlineKeyboardButton('❌Отменить', callback_data='mail_cancel')

btn_mailing = InlineKeyboardMarkup()
btn_mailing.add(picture)
btn_mailing.row(confirm, cancel)

confirm = InlineKeyboardButton('✅Подтвердить', callback_data='photo_confirm')
cancel = InlineKeyboardButton('❌Отменить', callback_data='photo_cancel')

btn_photo_mailing = InlineKeyboardMarkup()
btn_photo_mailing.row(confirm, cancel)