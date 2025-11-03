from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils import timezone

from applications.core.models import User
from .serializers import UserSerializer
from .services import send_verification_email


class RegisterView(generics.CreateAPIView):
    """
    Endpoint para registro de novos usuários.
    Após o registro, o usuário é criado como inativo e um e-mail de verificação é enviado.
    """
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        user.is_active = False  # Desativa o usuário até a verificação do e-mail
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
    """
    Endpoint para login. Retorna um par de tokens de acesso e atualização.
    Impede o login de usuários que não verificaram o e-mail.
    """
    serializer_class = CustomTokenObtainPairSerializer


class EmailVerificationView(APIView):
    """
    Endpoint para verificar o e-mail de um usuário com o código enviado.
    """
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
            # Não revele que o usuário não existe por segurança
            pass
        else:
            subject = "Seu código de redefinição de senha"
            message = "Seu código para redefinir a senha é: {code}"
            send_verification_email(user, subject, message)

        return Response({'message': 'Se um usuário com este e-mail existir, um código de verificação foi enviado.'}, status=status.HTTP_200_OK)


class PasswordResetValidateCodeView(APIView):
    """
    Endpoint para validar o código de redefinição de senha.
    Valida se o código está correto e não expirou, antes de permitir a redefinição da senha.
    """
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
        user.is_email_verified = True # A redefinição de senha também pode verificar o e-mail
        user.is_active = True
        user.save()

        return Response({'message': 'Senha redefinida com sucesso.'}, status=status.HTTP_200_OK)
