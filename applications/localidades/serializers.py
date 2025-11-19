from rest_framework import serializers
from .models import Estado, Cidade

class EstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estado
        fields = ('id', 'nome', 'uf')

class CidadeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cidade
        fields = ('id', 'nome', 'estado')
