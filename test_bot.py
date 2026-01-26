import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("START COMMAND RECEIVED")
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

if __name__ == '__main__':
    TOKEN = '8295315385:AAHdunV0gqw0tjGgPDCPuncGV8QjLOJgyds'
    application = ApplicationBuilder().token(TOKEN).build()
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    print("Minimal bot is starting...")
    application.run_polling()
