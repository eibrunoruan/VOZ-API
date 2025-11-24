from rest_framework import generics, status, serializers
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils import timezone

from applications.core.models import User
from .serializers import UserSerializer
from .services import send_verification_email

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        user.is_active = False
        user.save()

        subject = "Bem-vindo ao Voz do Povo! Ative sua conta."
        message = "Seu código de ativação é: {code}"
        send_verification_email(user, subject, message)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        if not self.user.is_email_verified:
            raise serializers.ValidationError({'detail': 'O e-mail ainda não foi verificado.'})
        return data

class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class EmailVerificationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        code = request.data.get('code')

        if not email or not code:
            return Response({'error': 'E-mail e código são obrigatórios.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Usuário não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        if user.is_email_verified:
            return Response({'message': 'Este e-mail já foi verificado.'}, status=status.HTTP_200_OK)

        if user.verification_code != code:
            return Response({'error': 'Código de verificação inválido.'}, status=status.HTTP_400_BAD_REQUEST)

        if user.code_expires_at < timezone.now():
            return Response({'error': 'O código de verificação expirou.'}, status=status.HTTP_400_BAD_REQUEST)

        user.is_active = True
        user.is_email_verified = True
        user.verification_code = None
        user.code_expires_at = None
        user.save()

        return Response({'message': 'E-mail verificado com sucesso! Você já pode fazer o login.'}, status=status.HTTP_200_OK)

class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'E-mail é obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            pass
        else:
            subject = "Seu código de redefinição de senha"
            message = "Seu código para redefinir a senha é: {code}"
            send_verification_email(user, subject, message)

        return Response({'message': 'Se um usuário com este e-mail existir, um código de verificação foi enviado.'}, status=status.HTTP_200_OK)

class PasswordResetValidateCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        code = request.data.get('code')

        if not email or not code:
            return Response({'error': 'E-mail e código são obrigatórios.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Usuário não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        if user.verification_code != code:
            return Response({'error': 'Código de verificação inválido.'}, status=status.HTTP_400_BAD_REQUEST)

        if user.code_expires_at < timezone.now():
            return Response({'error': 'O código de verificação expirou.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'Código validado com sucesso. Você pode redefinir sua senha.'}, status=status.HTTP_200_OK)

class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        code = request.data.get('code')
        password = request.data.get('password')

        if not all([email, code, password]):
            return Response({'error': 'E-mail, código e nova senha são obrigatórios.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Usuário não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        if user.verification_code != code:
            return Response({'error': 'Código de verificação inválido.'}, status=status.HTTP_400_BAD_REQUEST)

        if user.code_expires_at < timezone.now():
            return Response({'error': 'O código de verificação expirou.'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(password)
        user.verification_code = None
        user.code_expires_at = None
        user.is_email_verified = True
        user.is_active = True
        user.save()

        return Response({'message': 'Senha redefinida com sucesso.'}, status=status.HTTP_200_OK)

class MeView(APIView):
    """
    Endpoint para obter informações do usuário autenticado.
    GET /api/auth/me/
    Retorna: username, email, first_name, last_name, is_email_verified, date_joined
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, *args, **kwargs):
        """
        Atualiza informações do usuário autenticado.
        Campos permitidos: first_name, last_name, username
        """
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, *args, **kwargs):
        """
        Atualiza parcialmente informações do usuário autenticado.
        """
        return self.put(request, *args, **kwargs)
