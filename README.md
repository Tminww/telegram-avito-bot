# Telegram Avito Bot
### Запуск:
Максимально просто:

Создайте `.env` файл и укажите в нем токен Telegram бота:
`BOT_API_TOKEN=123456:TokenTokenTokenToken`
  
  Запустите используя Docker Compose:
`docker-compose up`  
 
 Видео:
 https://youtu.be/2WBQMD3EOhs

```bash
python3 venv .venv
source .venv/bin/activate
poetry install --no-root
docker compose up -d --build
docker cp src/database/database.sql avito-postgres:/tmp/database.sql
docker exec -it avito-postgres psql -U postgres -d avito -a -f /tmp/database.sql
```

```bash
uvicorn src.app:app --reload --host 0.0.0.0 --port 8000
python -m src.telegram.bot
python -m src.avito.parser

```



