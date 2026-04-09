from telegram.ext import Application, CommandHandler, MessageHandler, filters

from bot import config
from bot import handlers


def main() -> None:
    app = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", handlers.start))
    app.add_handler(CommandHandler("model", handlers.model))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.message))
    app.run_polling()


if __name__ == "__main__":
    main()
