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
        denuncias_candidatas = Denuncia.objects.filter(
            categoria=categoria,
            status__in=[Denuncia.Status.ABERTA, Denuncia.Status.EM_ANALISE]
        ).order_by('-data_criacao')

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
        
        denuncia_data = {
            'autor': user if user else None,
            'autor_convidado': autor_convidado if not user else None,
            **validated_data
        }
        nova_denuncia = Denuncia.objects.create(**denuncia_data)
        
        logger.info(f"Nova denuncia criada (ID: {nova_denuncia.id})")
        
        return nova_denuncia, True, False
