from rest_framework import serializers
from .models import User
from .telegram_utils import verify_telegram_code

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'phone_number', 'address')
        read_only_fields = ('role', 'phone_number')


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    telegram_code = serializers.CharField(
        write_only=True, 
        required=True, 
        help_text="Код из Telegram бота для подтверждения регистрации"
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'telegram_code')
        
    def validate_telegram_code(self, value):
        telegram_id = verify_telegram_code(value)
        if not telegram_id:
            raise serializers.ValidationError("Неверный или просроченный код подтверждения.")
        
        # Проверяем, не занят ли этот Telegram ID другим пользователем
        if User.objects.filter(telegram_id=telegram_id).exists():
            raise serializers.ValidationError("Этот Telegram аккаунт уже привязан к другому пользователю.")
            
        return telegram_id # Возвращаем ID, чтобы использовать его в create

    def create(self, validated_data):
        telegram_id = validated_data.pop('telegram_code')
        user = User.objects.create_user(**validated_data)
        user.telegram_id = telegram_id
        user.save()
        return user
