from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from bot import config
from bot import llm_client

_user_models: dict[int, str] = {}


def _get_model(user_id: int) -> str:
    return _user_models.get(user_id, config.DEFAULT_MODEL)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    model = _get_model(update.effective_user.id)
    await update.message.reply_text(
        f"Привет! Я бот с локальной LLM.\n"
        f"Отправь мне любое сообщение — я отвечу с помощью модели.\n"
        f"Текущая модель: {model}\n"
        f"Команда /model — сменить модель."
    )


async def model(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if context.args:
        requested = context.args[0]
        if requested not in config.AVAILABLE_MODELS:
            await update.message.reply_text(
                f"Модель не найдена. Доступные: {', '.join(config.AVAILABLE_MODELS)}"
            )
            return
        _user_models[user_id] = requested
        await update.message.reply_text(f"Модель переключена на: {requested}")
    else:
        current = _get_model(user_id)
        await update.message.reply_text(
            f"Текущая модель: {current}\n"
            f"Доступные: {', '.join(config.AVAILABLE_MODELS)}\n"
            f"Переключить: /model <название>"
        )


async def message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    if not text or not text.strip():
        return
    user_id = update.effective_user.id
    await update.message.chat.send_action(ChatAction.TYPING)
    response = await llm_client.generate(text.strip(), _get_model(user_id))
    await update.message.reply_text(response)
