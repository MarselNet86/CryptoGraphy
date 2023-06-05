translations = {
    'en': {
        'Успешная регистрация!': 'Successful register!',
        'Добро пожаловать!': 'Welcome!',
        'Выберите язык:': 'Select a language:',
        'Настройки приняты!': 'Settings accepted!',
        '🚩Нельзя ставить тот же регион!': '🚩You can\'t put the same region!',
        'Уже скоро...': 'Coming soon...',
        '📥Шифрование': '📥Encrypt',
        '📤Расшифрование': '📤Decrypt',
        '📚Инструкции': '📚Instructions',
        '⚙Настройки': '⚙Settings',
        '☎Поддержка': '☎Support',
        '⚠Неизвестный метод, возвращаю в главное меню!': '⚠Unknown method, I\'m returning to the main menu!',
        'Выберите тип шифрования\n\nМетоды:': 'Select Encryption Type\n\nMethods:',
        'Выберите тип расшифровки\n\nМетоды': 'Select Decryption Type\n\nMethods:',
        'Файл зашифрован!✅': 'ZAP! File encrypted!✅',
        'Файл расшифрован!✅': 'ZAP! File encrypted!✅',
        '🔙Действие отменено': '🔙Action canceled',
        '📂Зашифровываем данные...\n\n⏳Пожалуйста, подождите!': '📂Encrypting the data...\n\n⏳Please wait!',
        '✅Файл успешно зашифрован!': '✅The file has been successfully encrypted!',
        '🔑Введите ключ расшифрования:': '🔑 Enter the decryption key:',
        '🚫Ошибка при расшифровке файла!\n\n❗Ваш файл поврежден или имеет не верный ключ расшифровки!': '🚫Error decrypting the file!\n\n❗Your file is corrupted or has an incorrect decryption key!',
        '❌Отмена': '❌Cancel'
    }
}


def _(text, lang='ru'):
    if lang == 'ru':
        return text
    else:
        global translations
        try:
            return translations[lang].get(text, text)
        except:
            return text

