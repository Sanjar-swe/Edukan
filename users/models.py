from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ADMIN = 'admin'
    CLIENT = 'client'
    ROLE_CHOICES = (
        (ADMIN, 'Admin'),
        (CLIENT, 'Client'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=CLIENT, verbose_name="Rolı")
    phone_number = models.CharField(max_length=15, verbose_name="Telefon nomeri", blank=True, null=True)
    telegram_id = models.BigIntegerField(unique=True, verbose_name="Telegram ID", blank=True, null=True)
    address = models.TextField(verbose_name="Manzil", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Jaratılǵan waqtı")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ózgertilgen waqtı") 
    class Meta:
        verbose_name = 'Paydalanıwshı'
        verbose_name_plural = 'Paydalanıwshılar'
        ordering = ['-created_at']
    def __str__(self):
        return self.username


class TelegramAuthSession(models.Model):
    code = models.CharField(max_length=6, verbose_name="Tasdıqlaw kodı")
    telegram_id = models.BigIntegerField(verbose_name="Telegram ID")
    chat_id = models.BigIntegerField(verbose_name="Chat ID")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Jaratılǵan waqtı")
    is_used = models.BooleanField(default=False, verbose_name="Paydalanıldı")

    class Meta:
        verbose_name = 'Telegram Autentifikaciya'
        verbose_name_plural = 'Telegram Autentifikaciyalar'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.telegram_id} - {self.code}"