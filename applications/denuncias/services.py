from math import radians, sin, cos, sqrt, atan2
from django.db import transaction

from .models import Denuncia, ApoioDenuncia

SEARCH_RADIUS_METERS = 150
EARTH_RADIUS_KM = 6371.0

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calcula a distância em metros entre duas coordenadas de lat/lon.
    """
    # As coordenadas do modelo são Decimal, convertemos para float para o math
    lat1, lon1, lat2, lon2 = map(radians, [float(lat1), float(lon1), float(lat2), float(lon2)])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance_km = EARTH_RADIUS_KM * c
    return distance_km * 1000  # Converte para metros

def criar_ou_apoiar_denuncia(validated_data, user=None, autor_convidado=None):
    """
    Cria uma nova denúncia ou adiciona um apoio a uma denúncia existente.

    Verifica se já existe uma denúncia da mesma categoria dentro de um raio
    de X metros. Se existir e o usuário estiver autenticado, cria um ApoioDenuncia.
    Caso contrário, cria uma nova Denuncia.
    """
    new_lat = validated_data.get('latitude')
    new_lon = validated_data.get('longitude')
    categoria = validated_data.get('categoria')

    with transaction.atomic():
        denuncias_candidatas = Denuncia.objects.filter(categoria=categoria).order_by('-data_criacao')

        denuncia_proxima = None
        if user:  # Apenas usuários logados podem apoiar
            for denuncia in denuncias_candidatas:
                distancia = haversine_distance(
                    new_lat, new_lon,
                    denuncia.latitude, denuncia.longitude
                )
                if distancia <= SEARCH_RADIUS_METERS:
                    denuncia_proxima = denuncia
                    break

        if denuncia_proxima and user:
            if ApoioDenuncia.objects.filter(denuncia=denuncia_proxima, apoiador=user).exists():
                return denuncia_proxima, False, False

            ApoioDenuncia.objects.create(denuncia=denuncia_proxima, apoiador=user)
            return denuncia_proxima, False, True

        # Cria uma nova denúncia se não houver próxima ou se for convidado
        denuncia_data = {
            'autor': user if user else None,
            'autor_convidado': autor_convidado if not user else None,
            **validated_data
        }
        nova_denuncia = Denuncia.objects.create(**denuncia_data)
        return nova_denuncia, True, False
