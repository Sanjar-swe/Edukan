import random
import string
from django.utils import timezone
from datetime import timedelta
from .models import TelegramAuthSession

def generate_verification_code(length=6):
    """Generates a numeric verification code."""
    return ''.join(random.choices(string.digits, k=length))

def create_auth_session(telegram_id, chat_id):
    """Creates a new auth session with a unique code."""
    code = generate_verification_code()
    # Expire old sessions for this telegram_id
    TelegramAuthSession.objects.filter(telegram_id=telegram_id, is_used=False).update(is_used=True)
    
    session = TelegramAuthSession.objects.create(
        code=code,
        telegram_id=telegram_id,
        chat_id=chat_id
    )
    return session

def verify_telegram_code(code):
    """Verifies a code and returns the telegram_id if valid."""
    # Code is valid for 5 minutes
    expiry_time = timezone.now() - timedelta(minutes=5)
    
    session = TelegramAuthSession.objects.filter(
        code=code,
        is_used=False,
        created_at__gte=expiry_time
    ).first()
    
    if session:
        session.is_used = True
        session.save()
        return session.telegram_id
    
    return None
