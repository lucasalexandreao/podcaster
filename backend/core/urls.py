from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from accounts.views import RegisterView, PasswordResetRequestView 

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Rota de Login 
    path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    # Rota para atualizar o token
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Rota de Cadastro
    path('api/register/', RegisterView.as_view(), name='register'),

    # Rota de resetar senha
    path('api/password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
]