from rest_framework import generics
from django.contrib.auth.models import User
from .serializers import UserSerializer
from rest_framework.permissions import AllowAny
from django.contrib.auth.tokens import default_token_generator
from rest_framework.views import APIView
from rest_framework.response import Response

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer


class PasswordResetRequestView(APIView):
    permission_classes = (AllowAny,) 

    def post(self, request):
        email = request.data.get('email')
        user = User.objects.filter(email=email).first()
        
        if user:
            token = default_token_generator.make_token(user)
            
            # SIMULA O ENVIO DE E-MAIL 
            print("\n" + "="*50)
            print("E-MAIL DE RECUPERAÇÃO DE SENHA")
            print(f"Para: {email}")
            print(f"Link: http://localhost:5173/reset-password?user={user.id}&token={token}")
            print("="*50 + "\n")

        return Response({"message": "Se o e-mail estiver registado, receberá as instruções em breve."})