from rest_framework import serializers
from applications.core.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'password', 
            'first_name', 'last_name', 'is_email_verified', 
            'date_joined', 'last_login'
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'is_email_verified': {'read_only': True},
            'date_joined': {'read_only': True},
            'last_login': {'read_only': True},
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            password=validated_data['password']
        )
        return user
    
    def update(self, instance, validated_data):
        """
        Atualiza informações do usuário.
        Não permite atualizar password por este endpoint (use password-reset).
        """
        validated_data.pop('password', None)  # Remover password se enviado
        validated_data.pop('email', None)  # Não permite mudar email aqui
        
        return super().update(instance, validated_data)
