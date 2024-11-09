from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
import requests
import logging
from src.config import settings

API_TOKEN = settings.telegram_bot_token
bot = Bot(token=API_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

# Функция для проверки авторизации пользователя по Telegram ID
async def check_user_authorization(telegram_id):
    response = requests.get(f"http://localhost:8000/users/{telegram_id}")
    return response.status_code == 200

@dp.message(Command(commands=['start']))
async def start(message: types.Message):
    telegram_id = message.from_user.id
    username = message.from_user.username
    if not await check_user_authorization(telegram_id):
        response = requests.post("http://localhost:8000/users/", json={"telegram_id": telegram_id, "username": username})
        if response.status_code == 200:
            await message.reply("Вы успешно зарегистрированы!")
        else:
            await message.reply("Ошибка при регистрации. Повторите позже.")
    else:
        await message.reply("Вы уже зарегистрированы!")

from aiogram import types
from aiogram.filters import Command
import requests

@dp.message(Command(commands=['add_link']))
async def add_link(message: types.Message):
    telegram_id = message.from_user.id
    # Проверка авторизации пользователя
    if await check_user_authorization(telegram_id):
        # Получаем текст команды после команды '/add_link'
        text = message.text.strip()
        # Проверка, что ссылка была передана
        if len(text.split(maxsplit=1)) > 1:
            link = text.split(maxsplit=1)[1]
            # Здесь можно добавить проверку на валидность ссылки (если нужно)
            if link.startswith("https://www.avito.ru/") or link.startswith("https://avito.ru/"):
                response = requests.post("http://localhost:8000/links/", json={"telegram_id": telegram_id, "link": link})
                print(response.content)
                if response.status_code == 200:
                    await message.reply("Ссылка успешно добавлена!")
                else:
                    await message.reply(f"Не удалось добавить ссылку {link}. Попробуйте позже.")
            else:
                await message.reply("Пожалуйста, отправьте правильную ссылку (с https://avito.ru/ или https://www.avito.ru/).")
        else:
            await message.reply("Пожалуйста, укажите ссылку после команды, например: /add_link <ссылка>")
    else:
        await message.reply("Авторизуйтесь с помощью команды /start.")

@dp.message(Command(commands=['show_links']))
async def show_links(message: types.Message):
    telegram_id = message.from_user.id
    # Проверка авторизации пользователя
    if await check_user_authorization(telegram_id):
        # Запрос ссылок пользователя из FastAPI
        response = requests.get(f"http://localhost:8000/links/{telegram_id}")
        if response.status_code == 200:
            data = response.json()
            links = data.get("links", [])
            if links:
                # Форматируем ссылки в список
                links_message = "\n".join(links)
                await message.reply(f"Ваши ссылки:\n{links_message}")
            else:
                await message.reply("У вас пока нет добавленных ссылок.")
        else:
            await message.reply("Не удалось получить ссылки. Попробуйте позже.")
    else:
        await message.reply("Авторизуйтесь с помощью команды /start.")
        
@dp.message(Command(commands=['delete_link']))
async def delete_link(message: types.Message):
    telegram_id = message.from_user.id
    if await check_user_authorization(telegram_id):
        link = message.text.split(maxsplit=1)[1]
        response = requests.delete(f"http://localhost:8000/links/", json={"telegram_id": telegram_id, "link": link})
        if response.status_code == 200:
            await message.reply("Ссылка удалена!")
        else:
            await message.reply("Не удалось удалить ссылку.")
    else:
        await message.reply("Авторизуйтесь с помощью команды /start.")

# Главная асинхронная функция для запуска бота
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
