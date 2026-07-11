import logging
from telegram.ext import Application, CommandHandler

from config import BOT_TOKEN
from bot.database.db import init_db
from bot.handlers.conversation import get_conversation_handler, cancel

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    if not BOT_TOKEN or BOT_TOKEN == "your_telegram_bot_token_here":
        logger.error("BOT_TOKEN is not set. Edit .env with your real token.")
        return

    init_db()
    logger.info("Database initialized.")

    app = Application.builder().token(BOT_TOKEN).build()

    conv_handler = get_conversation_handler()
    app.add_handler(conv_handler)

    app.add_handler(CommandHandler("cancel", cancel))

    logger.info("Bot started polling...")
    app.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
