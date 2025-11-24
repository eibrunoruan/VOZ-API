from math import radians, sin, cos, sqrt, atan2
from django.db import transaction
import logging

from .models import Denuncia, ApoioDenuncia

SEARCH_RADIUS_METERS = 100
EARTH_RADIUS_KM = 6371.0

logger = logging.getLogger(__name__)

def haversine_distance(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [float(lat1), float(lon1), float(lat2), float(lon2)])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance_km = EARTH_RADIUS_KM * c
    return distance_km * 1000

def criar_ou_apoiar_denuncia(validated_data, user=None, autor_convidado=None):
    new_lat = validated_data.get('latitude')
    new_lon = validated_data.get('longitude')
    categoria = validated_data.get('categoria')

    logger.info(f"🆕 Nova denúncia/apoio recebido:")
    logger.info(f"   Categoria: {categoria.nome}")
    logger.info(f"   Coordenadas: {new_lat}, {new_lon}")
    logger.info(f"   Usuário: {user.username if user else autor_convidado}")

    with transaction.atomic():
        # Otimização: filtro geográfico aproximado (bounding box)
        # 100m ≈ 0.001 graus (aproximado)
        lat_delta = 0.001
        lon_delta = 0.001
        
        denuncias_candidatas = Denuncia.objects.filter(
            categoria=categoria,
            status__in=[Denuncia.Status.ABERTA, Denuncia.Status.EM_ANALISE],
            # Bounding box: reduz drasticamente candidatos antes do haversine
            latitude__gte=float(new_lat) - lat_delta,
            latitude__lte=float(new_lat) + lat_delta,
            longitude__gte=float(new_lon) - lon_delta,
            longitude__lte=float(new_lon) + lon_delta,
        ).only('id', 'latitude', 'longitude', 'titulo').order_by('-data_criacao')[:50]  # Limita a 50

        logger.info(f"🔍 Buscando denúncias similares:")
        logger.info(f"   Raio: {SEARCH_RADIUS_METERS}m")
        logger.info(f"   Categoria: {categoria.nome}")
        logger.info(f"   Candidatas encontradas: {denuncias_candidatas.count()}")

        denuncia_proxima = None
        distancia_encontrada = None
        
        for denuncia in denuncias_candidatas:
            distancia = haversine_distance(
                new_lat, new_lon,
                denuncia.latitude, denuncia.longitude
            )
            logger.debug(f"Denuncia ID {denuncia.id}: distancia = {distancia}m")
            
            if distancia <= SEARCH_RADIUS_METERS:
                denuncia_proxima = denuncia
                distancia_encontrada = distancia
                break

        if denuncia_proxima:
            logger.info(f"Denuncia similar encontrada (ID: {denuncia_proxima.id})")
            logger.info(f"Distancia: {distancia_encontrada:.2f} metros")
            logger.info(f"Adicionando apoio...")

            if user:
                apoio_existente = ApoioDenuncia.objects.filter(
                    denuncia=denuncia_proxima,
                    apoiador=user
                ).exists()
            else:
                apoio_existente = False

            if apoio_existente:
                logger.info(f"Usuario {user.username} ja apoiou esta denuncia")
                return denuncia_proxima, False, False

            ApoioDenuncia.objects.create(
                denuncia=denuncia_proxima,
                apoiador=user if user else None
            )
            
            logger.info(f"Apoio registrado com sucesso!")
            logger.info(f"Total de apoios: {denuncia_proxima.apoios.count()}")
            
            return denuncia_proxima, False, True

        logger.info(f"Nenhuma denuncia similar encontrada em {SEARCH_RADIUS_METERS}m")
        logger.info(f"Criando nova denuncia...")
        
        # Remover autor_convidado do validated_data para evitar conflito
        denuncia_data = validated_data.copy()
        denuncia_data.pop('autor_convidado', None)
        
        # Adicionar autor e autor_convidado explicitamente
        denuncia_data['autor'] = user if user else None
        denuncia_data['autor_convidado'] = autor_convidado if not user else None
        
        nova_denuncia = Denuncia.objects.create(**denuncia_data)
        
        logger.info(f"Nova denuncia criada (ID: {nova_denuncia.id})")
        logger.info(f"Autor: {nova_denuncia.autor or nova_denuncia.autor_convidado}")
        
        return nova_denuncia, True, False
