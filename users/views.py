from rest_framework import generics, permissions, status, serializers
import logging
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from .serializers import RegistrationSerializer, UserSerializer
from .models import User
from .telegram_utils import verify_telegram_code
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, extend_schema_view

# JWT Views with Swagger tags
@extend_schema_view(
    post=extend_schema(
        tags=['0. Paydalanıwshılar (Users & Auth)'],
        summary="Kiriw (Login)",
        description="Sistemanı paydalanıw ushın login hám paroldi jiberiń. \n\n[Info For Backender]: JWT Authentication"
    )

)
class DecoratedTokenObtainPairView(TokenObtainPairView):
    pass

@extend_schema_view(
    post=extend_schema(
        tags=['0. Paydalanıwshılar (Users & Auth)'],
        summary="Token jańalaw",
        description="Access tokendi jańalaw ushın refresh tokendi jiberiń. \n\n[Info For Backender]: JWT Refresh Mechanism"
    )

)
class DecoratedTokenRefreshView(TokenRefreshView):
    pass

# Регистрация нового пользователя
@extend_schema(
    tags=['0. Paydalanıwshılar (Users & Auth)'],
    summary="Dizimnen ótiw",
    description="Dizimden ótiw ushın maǵlıwmatlardı jiberiń. \n\n[Info For Backender]: Background task Celery (Welcome Email)"
)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegistrationSerializer
    throttle_scope = 'auth_attempt'

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)

# Просмотр и редактирование своего профиля
@extend_schema_view(
    get=extend_schema(
        tags=['0. Paydalanıwshılar (Users & Auth)'],
        summary="Profildi kóriw",
        description="Paydalanıwshı profil maǵlıwmatların kóriw. \n\n[Info For Backender]: Standard API Operation"
    ),
    patch=extend_schema(
        tags=['0. Paydalanıwshılar (Users & Auth)'],
        summary="Profildi ózgertiw",
        description="Profil maǵlıwmatların jańalaw. \n\n[Info For Backender]: Standard API Operation"
    )

)
class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ['get', 'patch', 'head', 'options']

    def get_object(self):
        return self.request.user

class TelegramLoginSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6, help_text="Код подтверждения из Telegram бота")

@extend_schema(
    tags=['0. Paydalanıwshılar (Users & Auth)'],
    summary="Telegram login",
    description="Telegram bot arqalı kirisiw kodın jiberiń. \n\n[Info For Backender]: OTP Verification via Telegram"
)

class TelegramLoginView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = TelegramLoginSerializer
    throttle_scope = 'auth_attempt'
    
    def post(self, request, *args, **kwargs):
        code = request.data.get('code')
        if not code:
            return Response({'error': 'Code is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        telegram_id, phone_number = verify_telegram_code(code)
        logger = logging.getLogger(__name__)
        logger.info(f"Telegram verification: code={code}, id={telegram_id}, phone={phone_number}")
        
        if not telegram_id:
            return Response({'error': 'Invalid or expired code'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Find or create user
        user, created = User.objects.get_or_create(
            telegram_id=telegram_id,
            defaults={'username': f'tg_{telegram_id}'}
        )
        logger.info(f"User found/created: {user.username}, created={created}, phone_before={user.phone_number}")
        
        # Update phone number if provided and not set
        if phone_number:
            if not user.phone_number or user.phone_number == "":
                user.phone_number = phone_number
                user.save()
                logger.info(f"Updated phone number for user {user.username} to {phone_number}")
            else:
                logger.info(f"User {user.username} already has a phone number: {user.phone_number}")
        else:
            logger.info(f"No phone number provided in this Telegram session")
        
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'created': created,
            'user': UserSerializer(user).data
        })