-- database.sql
DROP TABLE users CASCADE;
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    telegram_id INTEGER UNIQUE NOT NULL,
    username TEXT
);
DROP TABLE links CASCADE;
CREATE TABLE IF NOT EXISTS links (
    id SERIAL PRIMARY KEY,
    telegram_id INTEGER NOT NULL,
    link TEXT NOT NULL
);
DROP TABLE responses CASCADE;
CREATE TABLE IF NOT EXISTS responses (
    id SERIAL PRIMARY KEY,
    link_id INTEGER NOT NULL REFERENCES links(id),
    response_hash TEXT NOT NULL,  -- Хеш последнего содержимого
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);