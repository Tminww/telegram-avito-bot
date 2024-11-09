# database.py
import asyncpg
from src.config import settings
from src.schemas.schemas import User, LinkData, Notification
DATABASE_URL = settings.database_url

async def get_user_links():
    conn = await init_db()
    rows = await conn.fetch("SELECT telegram_id, link FROM links")
    await conn.close()
    return [(row['user_id'], row['link']) for row in rows]

async def get_last_content(user_id, url):
    conn = await init_db()
    result = await conn.fetchval("SELECT response_hash FROM responses WHERE link_id = (SELECT id FROM links WHERE user_id = $1 AND link = $2)", user_id, url)
    await conn.close()
    return result

async def update_last_content(user_id, url, new_hash):
    conn = await init_db()
    await conn.execute("""
        INSERT INTO responses (link_id, response_hash) VALUES (
            (SELECT id FROM links WHERE user_id = $1 AND link = $2), $3
        ) ON CONFLICT (link_id) DO UPDATE SET response_hash = $3, last_updated = CURRENT_TIMESTAMP
    """, user_id, url, new_hash)
    await conn.close()

async def insert_user(user: User) -> dict:
    conn = await init_db()
    await conn.execute("INSERT INTO users (telegram_id, username) VALUES ($1, $2) ON CONFLICT DO NOTHING", user.telegram_id, user.username)
    await conn.close()
    return {"status": "User registered"}

async def select_user(user_id: int) -> dict:
    conn = await init_db()
    user = await conn.fetchrow("SELECT * FROM users WHERE telegram_id = $1", user_id)
    await conn.close()
    return user

async def insert_link(link_data: LinkData) -> dict:
    conn = await init_db()
    await conn.execute("INSERT INTO links (telegram_id, link) VALUES ($1, $2)", link_data.user_id, link_data.link)
    await conn.close()
    return {"status": "Link added"}

async def delete_link(link_data: LinkData) -> dict:
    conn = await init_db()
    await conn.execute("DELETE FROM links WHERE telegram_id = $1 AND link = $2", link_data.user_id, link_data.link)
    await conn.close()
    return {"status": "Link deleted"}


async def init_db():
    return await asyncpg.connect(DATABASE_URL)