from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, executor
from config import token
import asyncio

bot = Bot(token=token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

if __name__ == '__main__':
    from handlers import dp
    executor.start_polling(dp, skip_updates=True)