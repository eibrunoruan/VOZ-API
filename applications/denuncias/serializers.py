from rest_framework import serializers
from .models import Categoria, Denuncia, ApoioDenuncia, Comentario
from applications.autenticacao.serializers import UserSerializer

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'

class DenunciaSerializer(serializers.ModelSerializer):
    autor = UserSerializer(read_only=True, required=False)
    total_apoios = serializers.SerializerMethodField()
    autor_convidado = serializers.CharField(max_length=150, required=False, allow_blank=True)

    class Meta:
        model = Denuncia
        fields = [
            'id', 'titulo', 'descricao', 'autor', 'autor_convidado', 'categoria', 'cidade', 'estado',
            'foto', 'endereco', 'latitude', 'longitude', 'jurisdicao', 'status',
            'data_criacao', 'total_apoios'
        ]
        read_only_fields = ('autor', 'data_criacao')

    def get_total_apoios(self, obj):
        return obj.apoios.count()

    def validate(self, data):
        user = self.context['request'].user
        autor_convidado = data.get('autor_convidado')

        if user.is_authenticated:
            if autor_convidado:
                # Não faz sentido ter um autor convidado se o usuário está logado
                raise serializers.ValidationError('Usuários autenticados não devem fornecer um nome de convidado.')
            return data
        
        if not autor_convidado:
            raise serializers.ValidationError('É necessário fornecer um nome de convidado para usuários não autenticados.')
            
        return data

class ApoioDenunciaSerializer(serializers.ModelSerializer):
    apoiador = UserSerializer(read_only=True)

    class Meta:
        model = ApoioDenuncia
        fields = '__all__'
        read_only_fields = ('apoiador', 'data_apoio')

    def create(self, validated_data):
        validated_data['apoiador'] = self.context['request'].user
        return super().create(validated_data)

class ComentarioSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Comentario.
    """
    autor = UserSerializer(read_only=True, required=False)
    autor_convidado = serializers.CharField(max_length=150, required=False)

    class Meta:
        model = Comentario
        fields = ['id', 'denuncia', 'autor', 'autor_convidado', 'texto', 'data_criacao']
        read_only_fields = ('id', 'autor', 'data_criacao')