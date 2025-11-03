from math import radians, sin, cos, sqrt, atan2
from django.db import transaction
import logging

from .models import Denuncia, ApoioDenuncia

# ✅ CORREÇÃO 1: Raio de agrupamento reduzido para 100 metros
SEARCH_RADIUS_METERS = 100  # Alterado de 150m para 100m
EARTH_RADIUS_KM = 6371.0

logger = logging.getLogger(__name__)

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

    REGRAS DE AGRUPAMENTO:
    - ✅ Mesma categoria
    - ✅ Raio de 100 metros
    - ✅ Status não resolvido
    - ✅ Permite apoio de usuários autenticados E convidados

    Retorna:
        tuple: (denuncia, created_denuncia, created_apoio)
            - denuncia: objeto Denuncia (nova ou existente)
            - created_denuncia: True se criou nova denúncia
            - created_apoio: True se criou novo apoio
    """
    new_lat = validated_data.get('latitude')
    new_lon = validated_data.get('longitude')
    categoria = validated_data.get('categoria')

    logger.info(f"🆕 Nova denúncia/apoio recebido:")
    logger.info(f"   Categoria: {categoria.nome}")
    logger.info(f"   Coordenadas: {new_lat}, {new_lon}")
    logger.info(f"   Usuário: {user.username if user else autor_convidado}")

    with transaction.atomic():
        # ✅ CORREÇÃO 2: Buscar denúncias da MESMA CATEGORIA e não resolvidas
        denuncias_candidatas = Denuncia.objects.filter(
            categoria=categoria,
            status__in=[Denuncia.Status.ABERTA, Denuncia.Status.EM_ANALISE]  # Não agrupa com resolvidas
        ).order_by('-data_criacao')

        logger.info(f"🔍 Buscando denúncias similares:")
        logger.info(f"   Raio: {SEARCH_RADIUS_METERS}m")
        logger.info(f"   Categoria: {categoria.nome}")
        logger.info(f"   Candidatas encontradas: {denuncias_candidatas.count()}")

        denuncia_proxima = None
        distancia_encontrada = None
        
        # Buscar denúncia próxima (tanto para usuários quanto convidados)
        for denuncia in denuncias_candidatas:
            distancia = haversine_distance(
                new_lat, new_lon,
                denuncia.latitude, denuncia.longitude
            )
            logger.debug(f"   Denúncia #{denuncia.id}: {distancia:.2f}m")
            
            if distancia <= SEARCH_RADIUS_METERS:
                denuncia_proxima = denuncia
                distancia_encontrada = distancia
                break

        # ✅ CORREÇÃO 3: Se encontrou denúncia próxima, criar apoio
        if denuncia_proxima:
            logger.info(f"✅ Denúncia similar encontrada (ID #{denuncia_proxima.id})")
            logger.info(f"   Distância: {distancia_encontrada:.2f} metros")
            logger.info(f"   Adicionando apoio...")

            # Verificar se já existe apoio deste usuário/convidado
            if user:
                # Usuário autenticado - verificar por apoiador
                apoio_existente = ApoioDenuncia.objects.filter(
                    denuncia=denuncia_proxima,
                    apoiador=user
                ).exists()
            else:
                # Convidado - não verificar duplicata (pode apoiar múltiplas vezes)
                # Isso permite que diferentes convidados apoiem, mesmo que usem o mesmo nome
                apoio_existente = False

            if apoio_existente:
                logger.info(f"⚠️  Usuário {user.username} já apoiou esta denúncia")
                return denuncia_proxima, False, False

            # Criar apoio
            ApoioDenuncia.objects.create(
                denuncia=denuncia_proxima,
                apoiador=user if user else None
            )
            
            logger.info(f"✅ Apoio registrado com sucesso!")
            logger.info(f"   Total de apoios: {denuncia_proxima.apoios.count()}")
            
            return denuncia_proxima, False, True

        # Não encontrou denúncia similar - criar nova
        logger.info(f"✅ Nenhuma denúncia similar encontrada em {SEARCH_RADIUS_METERS}m")
        logger.info(f"   Criando nova denúncia...")
        
        denuncia_data = {
            'autor': user if user else None,
            'autor_convidado': autor_convidado if not user else None,
            **validated_data
        }
        nova_denuncia = Denuncia.objects.create(**denuncia_data)
        
        logger.info(f"✅ Nova denúncia criada (ID #{nova_denuncia.id})")
        
        return nova_denuncia, True, False
