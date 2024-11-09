# parser.py
import asyncio
import aiohttp
import hashlib
import requests
from src.database.database import get_user_links, get_last_content, update_last_content

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

async def parse_and_check_updates(user_id, url):
    async with aiohttp.ClientSession() as session:
         # Получаем HTML-страницу
        html = await fetch(session, url)
        
        # Создаем хеш нового контента
        new_content_hash = hashlib.sha256(html.encode()).hexdigest()

        # Получаем хеш старого контента из базы данных
        last_hash = await get_last_content(user_id, url)  # Используем await

        if new_content_hash != last_hash:
            update_last_content(user_id, url, new_content_hash)
            notification_data = {"user_id": user_id, "message": f"Обновления по ссылке: {url}"}
            requests.post("http://localhost:8000/notify", json=notification_data)

async def run_parser():
    while True:
        tasks = []
         # Получаем все ссылки для пользователей (теперь с await)
        user_links = await get_user_links()  # Используем await

        # Создаем задачи для проверки обновлений
        for user_id, url in user_links:
            tasks.append(parse_and_check_updates(user_id, url))
        
        # Ожидаем выполнения всех задач
        await asyncio.gather(*tasks)

        # Засыпаем на 60 секунд перед следующим циклом
        await asyncio.sleep(40)

asyncio.run(run_parser())