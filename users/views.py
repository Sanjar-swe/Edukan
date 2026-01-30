from rest_framework import generics, permissions, status, serializers
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
    post=extend_schema(tags=['0. Paydalanıwshılar (Users & Auth)'])
)
class DecoratedTokenObtainPairView(TokenObtainPairView):
    pass

@extend_schema_view(
    post=extend_schema(tags=['0. Paydalanıwshılar (Users & Auth)'])
)
class DecoratedTokenRefreshView(TokenRefreshView):
    pass

# Регистрация нового пользователя
@extend_schema(tags=['0. Paydalanıwshılar (Users & Auth)'])
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
@extend_schema(tags=['0. Paydalanıwshılar (Users & Auth)'])
class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user

class TelegramLoginSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6, help_text="Код подтверждения из Telegram бота")

@extend_schema(tags=['0. Paydalanıwshılar (Users & Auth)'])
class TelegramLoginView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = TelegramLoginSerializer
    throttle_scope = 'auth_attempt'
    
    def post(self, request, *args, **kwargs):
        code = request.data.get('code')
        if not code:
            return Response({'error': 'Code is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        telegram_id, phone_number = verify_telegram_code(code)
        if not telegram_id:
            return Response({'error': 'Invalid or expired code'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Find or create user
        user, created = User.objects.get_or_create(
            telegram_id=telegram_id,
            defaults={'username': f'tg_{telegram_id}'}
        )
        
        # Update phone number if provided and not set
        if phone_number and not user.phone_number:
            user.phone_number = phone_number
            user.save()
        
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'created': created,
            'user': UserSerializer(user).data
        })