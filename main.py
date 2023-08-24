import asyncio
from aiogram import Bot, Dispatcher, types, executor
from dotenv import load_dotenv
import os

load_dotenv()
bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher(bot=bot)

@dp.message_handler(commands=['start'])#обработчик команды
async def cmd_start(message: types.message):
    await message.answer(f'Добрый день, {message.from_user.first_name} {message.from_user.last_name}')# функция ответа юзеру

@dp.message_handler()
async def answer(message: types.message):
    await message.reply('Нажми /start для начала работы бота') #функция ответ на сообщение пользователя


if __name__ == '__main__':
    executor.start_polling(dp)#запуск бота


