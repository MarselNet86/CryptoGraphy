import psycopg2
import pandas as pd
from config import host, user, password, db_name, port
import warnings


class Database:
    def __init__(self, host, user, password, database, port):
        self.connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port
        )
        self.connection.autocommit = True

    def get_version(self):
        """Получить версию СУБД PostgreSQL"""
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            print(f'Server version: {cursor.fetchone()[0]}')

    def user_exists(self, user_id):
        """Проверить пользователя на существование в таблице"""
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE user_id = %s", [user_id])
            result = cursor.fetchall()
            return bool(len(result))

    def add_user(self, user_id, lang):
        """Добавить нового пользователя в таблицу"""
        with self.connection.cursor() as cursor:
            cursor.execute("INSERT INTO users (user_id, lang) VALUES (%s, %s)", [user_id, lang])

    def get_lang(self, user_id):
        """Получить регион пользователя"""
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT lang FROM users WHERE user_id = %s", [user_id])
            result = cursor.fetchone()[0]
            return result

    def update_lang(self, lang, user_id):
        """Обновить регион пользователя"""
        with self.connection.cursor() as cursor:
            cursor.execute("UPDATE users SET lang = %s WHERE user_id = %s", [lang, user_id])

    def mailing(self):
        """Получить user_id и кол-во пользователей для рассылки"""
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT user_id FROM users")
            user_ids = cursor.fetchall()
        return user_ids, len(user_ids)

    def get_statistics(self):
        """Получить кол-во пользователей в боте"""
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(id) FROM users")
            result = cursor.fetchone()[0]
        return result

    def export_users(self, file_path):
        """Выгрузить данные таблицы users в Excel файл"""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # Отключение предупреждений
            query = "SELECT id, user_id, lang FROM users"
            df = pd.read_sql_query(query, self.connection)
            df.to_excel(file_path, index=False)


db = Database(host, user, password, db_name, port)
