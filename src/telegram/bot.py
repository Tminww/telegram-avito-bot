from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters.state import StateFilter


import requests
import logging
from src.config import settings

API_TOKEN = settings.telegram_bot_token
bot = Bot(token=API_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)


# Определяем состояния
class Form(StatesGroup):
    waiting_for_link_to_add = State()  # Состояние для добавления ссылки
    waiting_for_link_to_delete = State()  # Состояние для удаления ссылки
    confirming_deletion = State()  # Состояние для подтверждения удаления


def get_cancel_keyboard():
    buttons = [
        [KeyboardButton(text='/cancel')]
    ]
    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=buttons  # Передаем кнопки здесь
    )
    return keyboard

# Создаем клавиатуру с кнопками
def get_main_keyboard():
    buttons = [
        [KeyboardButton(text='/start')],        # Каждая кнопка на своей строке
        [KeyboardButton(text='/add_link')],
        [KeyboardButton(text='/show_links')],
        [KeyboardButton(text='/delete_link')],
    ]
    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=buttons  # Передаем кнопки здесь
    )
    return keyboard



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
            await message.reply("Вы успешно зарегистрированы!", reply_markup=get_main_keyboard())
        else:
            await message.reply("Ошибка при регистрации. Повторите позже.")
    else:
        await message.reply("Вы уже зарегистрированы!", reply_markup=get_main_keyboard())

# Обработчик команды /add_link
@dp.message(Command(commands=['add_link']))
async def add_link(message: types.Message, state: FSMContext):
    await message.reply(
        "Пожалуйста, отправьте мне ссылку. Если вы передумали, отправьте /cancel.",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(Form.waiting_for_link_to_add)

# Обработчик ввода ссылки
@dp.message(StateFilter(Form.waiting_for_link_to_add))
async def handle_link_input(message: types.Message, state: FSMContext):
    link = message.text

    if link == '/cancel':
        await cancel_input(message, state)
        return
    
    # Проверка валидности ссылки
    if not link.startswith("http://") and not link.startswith("https://"):
        await message.reply("Это не похоже на ссылку. Пожалуйста, отправьте ссылку, начинающуюся с 'http://' или 'https://'. Если вы передумали, отправьте /cancel.")
        return

    # Сохранение ссылки
    response = requests.post("http://localhost:8000/links/", json={"telegram_id": message.from_user.id, "link": link})
    if response.status_code == 200:
        await message.reply("Ссылка успешно сохранена!", reply_markup=get_main_keyboard())
    else:
        await message.reply("Ошибка при сохранении ссылки. Попробуйте позже.", reply_markup=get_main_keyboard())

    # Завершение состояния
    await state.clear()




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
        
# Хендлер для /delete_link
@dp.message(Command(commands=['delete_link']))
async def cmd_delete_link(message: types.Message, state: FSMContext):
    await state.set_state(Form.waiting_for_link_to_delete)
    await message.reply("Пожалуйста, отправьте ссылку, которую хотите удалить. Если вы передумали, отправьте /cancel.",
        reply_markup=get_cancel_keyboard())

# Хендлер для обработки полученной ссылки (когда пользователь отправил ссылку)
@dp.message(StateFilter(Form.waiting_for_link_to_delete))
async def process_delete_link(message: types.Message, state: FSMContext):
    user_link = message.text.strip()

    if user_link == '/cancel':
        await cancel_input(message, state)
        return
    # Проверяем, существует ли ссылка в базе данных
    response = requests.get(f"http://localhost:8000/links/{message.from_user.id}/{user_link}")
    
    if response.status_code == 200:
        # Если ссылка найдена, спрашиваем подтверждение
        await state.update_data(link=user_link)
        await state.set_state(Form.confirming_deletion)
        await message.reply(f"Вы уверены, что хотите удалить эту ссылку: {user_link}? (Да/Нет)")
    else:
        await message.reply("Эта ссылка не найдена в вашем списке. Попробуйте еще раз.")

# Хендлер для подтверждения удаления
@dp.message(StateFilter(Form.confirming_deletion))
async def confirm_deletion(message: types.Message, state: FSMContext):
    answer = message.text.strip().lower()

    if answer in ['да', 'yes']:
        # Получаем ссылку из состояния и выполняем удаление
        user_data = await state.get_data()
        user_link = user_data['link']

        response = requests.delete(f"http://localhost:8000/links/{message.from_user.id}/{user_link}")

        if response.status_code == 200:
            await message.reply(f"Ссылка {user_link} успешно удалена.")
        else:
            await message.reply("Произошла ошибка при удалении ссылки. Пожалуйста, попробуйте снова.")
        
        # Завершаем работу с состоянием
        await state.finish()

    elif answer in ['нет', 'no']:
        await message.reply("Удаление отменено.")
        await state.finish()
    else:
        await message.reply("Пожалуйста, ответьте 'Да' или 'Нет'.")

# Обработчик команды /cancel
@dp.message(Command(commands=['cancel']))
async def cancel_input(message: types.Message, state: FSMContext):
    # Проверяем, что пользователь находится в процессе ввода ссылки
    
    await state.clear()  # Сбрасываем состояние
    await message.reply("Ввод отменен.", reply_markup=get_main_keyboard())


# Главная асинхронная функция для запуска бота
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
