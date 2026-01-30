from django.urls import path
from .views import (RegisterView, ProfileView, TelegramLoginView, 
                    DecoratedTokenObtainPairView, DecoratedTokenRefreshView)

urlpatterns = [
    # JWT эндпоинты (Login)
    path('login/', DecoratedTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', DecoratedTokenRefreshView.as_view(), name='token_refresh'),
    # Пользовательские эндпоинты
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('telegram-login/', TelegramLoginView.as_view(), name='telegram-login'),
]
