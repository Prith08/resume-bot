import os
import time
import logging
import threading
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram.ext import Application, CommandHandler

from config import BOT_TOKEN
from bot.database.db import init_db
from bot.handlers.conversation import get_conversation_handler, cancel

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def log_message(self, format, *args):
        pass


def start_health_server():
    port = int(os.environ.get("PORT", 8000))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    logger.info(f"Health check server listening on port {port}")
    server.serve_forever()


def self_ping():
    url = os.environ.get("RENDER_EXTERNAL_URL")
    if not url:
        return
    while True:
        time.sleep(480)
        try:
            urllib.request.urlopen(url, timeout=10)
            logger.debug("Self-ping successful")
        except Exception as e:
            logger.warning(f"Self-ping failed: {e}")


def main():
    if not BOT_TOKEN or BOT_TOKEN == "your_telegram_bot_token_here":
        logger.error("BOT_TOKEN is not set. Edit .env with your real token.")
        return

    init_db()
    logger.info("Database initialized.")

    threading.Thread(target=start_health_server, daemon=True).start()
    threading.Thread(target=self_ping, daemon=True).start()

    app = Application.builder().token(BOT_TOKEN).build()

    conv_handler = get_conversation_handler()
    app.add_handler(conv_handler)

    app.add_handler(CommandHandler("cancel", cancel))

    logger.info("Bot started polling...")
    app.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
