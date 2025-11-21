from rest_framework import serializers
from .models import Categoria, Denuncia, ApoioDenuncia, Comentario
from applications.autenticacao.serializers import UserSerializer

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'

class DenunciaListSerializer(serializers.ModelSerializer):
    """
    Serializer otimizado para listagem de denúncias.
    Não inclui objetos nested pesados, apenas IDs e nomes.
    """
    total_apoios = serializers.IntegerField(read_only=True)  # Vem do annotate
    categoria_nome = serializers.CharField(source='categoria.nome', read_only=True)
    cidade_nome = serializers.CharField(source='cidade.nome', read_only=True)
    estado_nome = serializers.CharField(source='estado.nome', read_only=True)
    estado_sigla = serializers.CharField(source='estado.sigla', read_only=True)
    autor_nome = serializers.SerializerMethodField()

    class Meta:
        model = Denuncia
        fields = [
            'id', 'titulo', 'descricao', 'autor_nome', 'autor_convidado',
            'categoria', 'categoria_nome', 'cidade', 'cidade_nome',
            'estado', 'estado_nome', 'estado_sigla',
            'foto', 'endereco', 'latitude', 'longitude',
            'jurisdicao', 'status', 'data_criacao', 'total_apoios'
        ]
    
    def get_autor_nome(self, obj):
        if obj.autor:
            return obj.autor.get_full_name() or obj.autor.email
        return obj.autor_convidado or 'Anônimo'

class DenunciaSerializer(serializers.ModelSerializer):
    """
    Serializer completo para detalhes de denúncia (create, update, retrieve).
    """
    autor = UserSerializer(read_only=True, required=False)
    total_apoios = serializers.IntegerField(read_only=True, default=0)  # Vem do annotate
    autor_convidado = serializers.CharField(max_length=150, required=False, allow_blank=True)
    categoria_nome = serializers.CharField(source='categoria.nome', read_only=True)
    cidade_nome = serializers.CharField(source='cidade.nome', read_only=True)
    estado_nome = serializers.CharField(source='estado.nome', read_only=True)

    class Meta:
        model = Denuncia
        fields = [
            'id', 'titulo', 'descricao', 'autor', 'autor_convidado',
            'categoria', 'categoria_nome', 'cidade', 'cidade_nome',
            'estado', 'estado_nome', 'foto', 'endereco',
            'latitude', 'longitude', 'jurisdicao', 'status',
            'data_criacao', 'total_apoios'
        ]
        read_only_fields = ('autor', 'data_criacao', 'total_apoios')

    def validate(self, data):
        request = self.context.get('request')
        user = request.user if request else None
        autor_convidado = data.get('autor_convidado')

        # Usuário autenticado: não pode fornecer nome de convidado
        if user and user.is_authenticated:
            if autor_convidado:
                raise serializers.ValidationError('Usuários autenticados não devem fornecer um nome de convidado.')
            return data
        
        # Usuário não autenticado (guest): DEVE fornecer nome de convidado
        if not user or not user.is_authenticated:
            if not autor_convidado or autor_convidado.strip() == '':
                raise serializers.ValidationError('Usuários não autenticados devem fornecer um nome de convidado.')
            return data
        
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
    autor = UserSerializer(read_only=True, required=False)
    autor_convidado = serializers.CharField(max_length=150, required=False)

    class Meta:
        model = Comentario
        fields = ['id', 'denuncia', 'autor', 'autor_convidado', 'texto', 'data_criacao']
        read_only_fields = ('id', 'autor', 'data_criacao')