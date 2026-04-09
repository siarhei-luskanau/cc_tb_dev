# Telegram-бот с локальной LLM (Ollama)

Бот отвечает на сообщения в Telegram, используя локальную языковую модель через [Ollama](https://ollama.com).

## Требования

- Docker и docker-compose

## Запуск

1. Скопировать шаблон переменных окружения и вписать токен бота:
   ```bash
   cp .env.example .env
   ```
   Открыть `.env` и заменить `your_token_here` на токен от [@BotFather](https://t.me/BotFather).

2. Запустить сервисы:
   ```bash
   docker-compose up -d
   ```

3. Скачать модель (после того как Ollama запустилась):
   ```bash
   docker exec -it cc_tb_dev-ollama-1 ollama pull qwen3:0.6b
   ```

4. Открыть бота в Telegram и начать чат.

## Команды бота

| Команда | Описание |
|---|---|
| `/start` | Приветствие и текущая модель |
| `/model` | Показать текущую и доступные модели |
| `/model <название>` | Переключить модель |

## Доступные модели

- `qwen3:0.6b` (по умолчанию)
- `qwen3.5:0.5b`
- `gpt-oss:20b`

## Переменные окружения

| Переменная | Описание | По умолчанию |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | Токен бота (обязательно) | — |
| `OLLAMA_BASE_URL` | Адрес Ollama | `http://ollama:11434` |
| `DEFAULT_MODEL` | Модель по умолчанию | `qwen3:0.6b` |
| `AVAILABLE_MODELS` | Список моделей через запятую | `qwen3:0.6b,qwen3.5:0.5b,gpt-oss:20b` |
