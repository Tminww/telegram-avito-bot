# Telegram Avito Bot

### Запуск:

Создайте `.env` файл и укажите в нем токен Telegram бота:

```bash
TELEGRAM_BOT_TOKEN=token
DB_HOST=avito-postgres
DB_PORT=5432
DB_NAME=avito
DB_USER=postgres
DB_PASS=postgres
```

Запустите используя Docker Compose:
`docker-compose up -d --build`

```bash
python3 venv .venv
source .venv/bin/activate
pip install poetry
poetry install --no-root
docker compose up -d --build
docker cp src/database/database.sql avito-postgres:/tmp/database.sql
docker exec -it avito-postgres psql -U postgres -d avito -a -f /tmp/database.sql
```

```bash
uvicorn src.gateway.app:app --reload --host 0.0.0.0 --port 8000
python -m src.telegram.bot
python -m src.avito.parser

```
