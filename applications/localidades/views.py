from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import AllowAny
from .models import Estado, Cidade
from .serializers import EstadoSerializer, CidadeSerializer

import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class EstadoViewSet(ReadOnlyModelViewSet):
    queryset = Estado.objects.all()
    serializer_class = EstadoSerializer
    permission_classes = [AllowAny]

class CidadeViewSet(ReadOnlyModelViewSet):
    queryset = Cidade.objects.all()
    serializer_class = CidadeSerializer
    permission_classes = [AllowAny]

class AnalisarLocalizacaoView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        latitude = request.query_params.get('latitude')
        longitude = request.query_params.get('longitude')

        if not latitude or not longitude:
            return Response(
                {'error': 'Os parâmetros "latitude" e "longitude" são obrigatórios.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        headers = {
            'User-Agent': settings.NOMINATIM_USER_AGENT
        }
        params = {
            'format': 'json',
            'lat': latitude,
            'lon': longitude,
            'zoom': 10,
            'addressdetails': 1
        }

        try:
            response = requests.get(settings.NOMINATIM_API_ENDPOINT, params=params, headers=headers, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            return Response(
                {'error': f'Erro ao contatar o serviço de geolocalização: {e}'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        data = response.json()
        address = data.get('address')

        if not address:
            return Response(
                {'error': 'Não foi possível encontrar um endereço para as coordenadas fornecidas.'},
                status=status.HTTP_404_NOT_FOUND
            )

        cidade_nome = address.get('city') or address.get('municipality') or address.get('town') or address.get('village') or address.get('county')
        estado_nome = address.get('state')
        
        categoria_osm = data.get('category')
        if categoria_osm == 'highway':
            jurisdicao_sugerida = 'FEDERAL'
        else:
            jurisdicao_sugerida = 'MUNICIPAL'

        estado_obj = None
        estado_id = None
        if estado_nome:
            estado_obj = Estado.objects.filter(nome__icontains=estado_nome).first()
            if estado_obj:
                estado_id = estado_obj.id

        cidade_obj = None
        cidade_id = None
        cidade_identificada = False
        
        if cidade_nome and estado_obj:
            cidade_obj = Cidade.objects.filter(
                nome__icontains=cidade_nome,
                estado=estado_obj
            ).first()
            if cidade_obj:
                cidade_id = cidade_obj.id
                cidade_identificada = True

        return Response({
            'cidade': cidade_nome,
            'cidade_id': cidade_id,
            'cidade_identificada': cidade_identificada,
            'estado': estado_nome,
            'estado_id': estado_id,
            'jurisdicao_sugerida': jurisdicao_sugerida,
            'dados_completos_osm': address
        })
