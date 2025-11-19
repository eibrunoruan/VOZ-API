from rest_framework import serializers
from .models import OfficialResponse

class OfficialResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfficialResponse
        fields = ['id', 'denuncia', 'entidade', 'texto', 'data_resposta']
        read_only_fields = ('id', 'entidade', 'data_resposta')

    def validate_denuncia(self, value):
        if OfficialResponse.objects.filter(denuncia=value).exists():
            raise serializers.ValidationError("Esta denúncia já possui uma resposta oficial.")
        return value