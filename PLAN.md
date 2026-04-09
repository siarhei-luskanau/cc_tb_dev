# План реализации: Telegram-бот с локальной LLM

## Параметры проекта

- **Язык**: Python 3.11+
- **Telegram-библиотека**: `python-telegram-bot` v20+ (async)
- **LLM-провайдер**: Ollama (локально)
- **Доступные модели**: `qwen3:0.6b`, `qwen3.5:0.8b`, `gpt-oss:20b`
- **Бонус**: команда `/model` для переключения модели
- **Инфраструктура**: Docker + docker-compose
- **Тесты**: нет

---

## Структура проекта

```
cc_tb_dev/
├── bot/
│   ├── __init__.py
│   ├── main.py          # Точка входа, инициализация и запуск бота
│   ├── config.py        # Конфигурация из переменных окружения
│   ├── handlers.py      # Обработчики сообщений и команд
│   └── llm_client.py    # HTTP-клиент для Ollama API
├── docker-compose.yml   # Оркестрация бота + Ollama
├── Dockerfile           # Образ бота
├── requirements.txt     # Python-зависимости
├── .env.example         # Шаблон переменных окружения
└── README.md            # Инструкция по запуску
```

---

## Шаги реализации

### Шаг 1 — `requirements.txt`
Зависимости:
- `python-telegram-bot[job-queue]>=20.0` — async Telegram Bot API polling
- `httpx>=0.27` — async HTTP для запросов к Ollama
- `python-dotenv>=1.0` — загрузка `.env` файла

### Шаг 2 — `bot/config.py`
Загрузка конфигурации из переменных окружения:
- `TELEGRAM_BOT_TOKEN` — токен бота (обязательно)
- `OLLAMA_BASE_URL` — адрес Ollama (по умолчанию `http://localhost:11434`)
- `DEFAULT_MODEL` — модель по умолчанию (по умолчанию `qwen3:0.6b`)
- `AVAILABLE_MODELS` — список доступных моделей через запятую

### Шаг 3 — `bot/llm_client.py`
Async HTTP-клиент для Ollama:
- Метод `generate(prompt: str, model: str) -> str`
- POST `{OLLAMA_BASE_URL}/api/generate` с `{"model": ..., "prompt": ..., "stream": false}`
- Возврат поля `response` из JSON-ответа
- Обработка ошибок: таймаут, недоступность Ollama → понятное сообщение пользователю

### Шаг 4 — `bot/handlers.py`
Обработчики Telegram:

**`/start`** — приветственное сообщение с описанием бота и текущей модели.

**`/model`** — без аргументов показывает текущую модель и список доступных. С аргументом `/model qwen3:0.6b` — переключает модель для этого пользователя (in-memory dict, без персистентности).

**Текстовые сообщения**:
1. Отправить "печатает..." (typing action)
2. Передать текст в `llm_client.generate()`
3. Вернуть ответ пользователю
4. При ошибке — вернуть понятное сообщение об ошибке

Хранение выбранной модели: `dict[user_id -> model_name]` в памяти (сбрасывается при перезапуске бота — соответствует требованию "без хранения состояния").

### Шаг 5 — `bot/main.py`
- Загрузка конфига через `config.py`
- Регистрация handlers
- Запуск polling (`Application.run_polling()`)

### Шаг 6 — `Dockerfile`
```
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY bot/ ./bot/
CMD ["python", "-m", "bot.main"]
```

### Шаг 7 — `docker-compose.yml`
Два сервиса:
- **`ollama`** — образ `ollama/ollama`, volume для моделей, порт 11434
- **`bot`** — собранный Dockerfile, зависит от `ollama`, env-файл `.env`

Startup: Ollama стартует первым, бот ждёт готовности через `depends_on` + healthcheck или retry-логику в `llm_client.py`.

### Шаг 8 — `.env.example`
```env
TELEGRAM_BOT_TOKEN=your_token_here
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_MODEL=qwen3:0.6b
AVAILABLE_MODELS=qwen3:0.6b,qwen3.5:0.8b,gpt-oss:20b
```

### Шаг 9 — `README.md`
Инструкция по запуску:
1. Установить Docker и docker-compose
2. Скопировать `.env.example` в `.env`, вписать токен
3. `docker-compose up -d`
4. Скачать модель: `docker exec -it ollama ollama pull qwen3:0.6b`
5. Начать чат с ботом в Telegram

---

## Поток данных

```
Пользователь → Telegram API
    → polling → handlers.py
        → llm_client.py → Ollama API (POST /api/generate)
            ← JSON response
        ← ответ LLM
    ← sendMessage → Telegram API
→ Пользователь
```

---

## Обработка ошибок

| Ситуация | Поведение |
|---|---|
| Ollama недоступна | "Сервис LLM временно недоступен. Попробуйте позже." |
| Таймаут запроса (>60с) | "Превышено время ожидания ответа от LLM." |
| Неизвестная модель в /model | "Модель не найдена. Доступные: ..." |
| Пустое сообщение | Игнорировать |

---

## Порядок выполнения (параллельно где возможно)

```
[1] requirements.txt
[2] bot/config.py
[3] bot/llm_client.py          ← зависит от [2]
[4] bot/handlers.py            ← зависит от [2], [3]
[5] bot/main.py                ← зависит от [4]
[6] bot/__init__.py
[7] Dockerfile                 ← зависит от [1]
[8] docker-compose.yml         ← зависит от [7]
[9] .env.example
[10] README.md
```
