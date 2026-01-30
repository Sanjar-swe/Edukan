import os
import sys
import django
import logging
import asyncio

# Set up Django environment
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
from django.conf import settings
from asgiref.sync import sync_to_async
from users.telegram_utils import create_auth_session

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a welcome message and requests contact."""
    user = update.effective_user
    logger.info(f"Start command received from user {user.id} ({user.first_name})")
    
    keyboard = [
        [KeyboardButton("📲 Kontaktı jiberiw / Отправить контакт", request_contact=True)]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

    message = (
        f"Assalawma áleykum, {user.first_name}! 👋\n\n"
        f"<b>Online Dúkan</b> rásmiy botına xosh kelipsiz.\n\n"
        "Tastıyıqlaw kodın alıw ushın tómendegi túymeni basıp kontaktıńızdı jiberiń:\n"
        "--------------------\n"
        "Добро пожаловать в официальный бот <b>Online Dúkan</b>.\n"
        "Для получения кода подтверждения нажмите кнопку ниже и отправьте свой контакт:"
    )
    
    try:
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='HTML')
        logger.info(f"Welcome message sent to user {user.id}")
    except Exception as e:
        logger.error(f"Error sending welcome message to {user.id}: {e}")

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles shared contact and sends the code."""
    user = update.effective_user
    logger.info(f"Contact received from user {user.id}")
    
    try:
        contact = update.message.contact
        user_id = user.id
        chat_id = update.effective_chat.id

        if not contact:
            logger.warning(f"Message from {user_id} does not contain a contact.")
            return

        logger.info(f"Contact details: phone={contact.phone_number}, user_id_in_contact={contact.user_id}")

        if contact.user_id != user_id:
            logger.warning(f"User {user_id} sent someone else's contact.")
            await update.message.reply_text("Iltimas, ózińizdiń kontaktıńızdı jiberiń / Пожалуйста, отправьте свой собственный контакт.")
            return

        logger.info(f"Proceeding to send verification code for user {user_id}")
        await send_verification_code(update, context, user_id, chat_id, contact.phone_number)
        
    except Exception as e:
        logger.error(f"Critical error in handle_contact for user {user.id}: {e}", exc_info=True)
        await update.message.reply_text("Keshirasiz, qátelik júz berdi. / Извините, произошла ошибка.")

async def login_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Quick command to get a new code."""
    logger.info(f"Login command received from user {update.effective_user.id}")
    await send_verification_code(update, context, update.effective_user.id, update.effective_chat.id)

async def send_verification_code(update_or_query, context, user_id, chat_id, phone_number=None):
    """Helper to generate and send/edit code message."""
    logger.info(f"Generating verification code for user {user_id}")
    try:
        session = await sync_to_async(create_auth_session)(user_id, chat_id, phone_number)
        logger.info(f"Auth session created: code={session.code} for user {user_id}")
    except Exception as e:
        logger.error(f"Error creating auth session for user {user_id}: {e}", exc_info=True)
        return

    message_text = (
        f"🔐 <b>Tastıyıqlaw kodı / Код подтверждения:</b>\n\n"
        f"<code>{session.code}</code>\n\n"
        "Bul kod 5 minut dawamında jaramlı. / Этот код действителен в течение 5 минут."
    )

    keyboard = [
        [
            InlineKeyboardButton("🌐 Saytqa ótiw / Перейти на сайт", url="http://127.0.0.1:8000/swagger/"),
            InlineKeyboardButton("🔄 Jańalaw / Обновить", callback_data="renew_code")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        if isinstance(update_or_query, Update) and update_or_query.message:
            await update_or_query.message.reply_text(message_text, reply_markup=reply_markup, parse_mode='HTML')
            logger.info(f"Verification code sent to user {user_id} via message")
        elif isinstance(update_or_query, CallbackQuery):
            await update_or_query.edit_message_text(message_text, reply_markup=reply_markup, parse_mode='HTML')
            logger.info(f"Verification code updated for user {user_id} via callback")
    except Exception as e:
        logger.error(f"Error sending/editing verification code for user {user_id}: {e}")

async def renew_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the Renew button click."""
    query = update.callback_query
    user_id = query.from_user.id
    logger.info(f"Renew button clicked by user {user_id}")
    
    try:
        await query.answer("Kod jańalanbaqta... / Код обновляется...")
        await send_verification_code(query, context, user_id, query.message.chat_id)
    except Exception as e:
        logger.error(f"Error in renew_callback for user {user_id}: {e}")

if __name__ == '__main__':
    logger.info("Starting bot script...")
    if not settings.TELEGRAM_BOT_TOKEN or settings.TELEGRAM_BOT_TOKEN == 'your-telegram-bot-token-here':
        logger.error("TELEGRAM_BOT_TOKEN is not set properly in .env")
    else:
        try:
            application = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()
            
            application.add_handler(CommandHandler('start', start))
            application.add_handler(CommandHandler('login', login_command))
            application.add_handler(MessageHandler(filters.CONTACT, handle_contact))
            application.add_handler(CallbackQueryHandler(renew_callback, pattern="^renew_code$"))
            
            logger.info("Bot is starting polling...")
            application.run_polling()
        except Exception as e:
            logger.error(f"Failed to start bot application: {e}", exc_info=True)
