#!/usr/bin/env python
"""
Script de teste para validar o sistema de agrupamento de denúncias

Testa:
1. Raio de 100 metros
2. Filtro por categoria
3. Apoio de convidados
4. Não agrupar denúncias resolvidas

Executar: python testar_agrupamento.py
"""

import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'voz_do_povo.settings')
django.setup()

from applications.denuncias.models import Denuncia, ApoioDenuncia, Categoria
from applications.denuncias.services import haversine_distance, SEARCH_RADIUS_METERS
from applications.localidades.models import Estado, Cidade
from applications.core.models import User

print("=" * 80)
print("🧪 TESTE DE AGRUPAMENTO DE DENÚNCIAS")
print("=" * 80)
print()

# Configurações
print(f"⚙️  Configurações:")
print(f"   Raio de agrupamento: {SEARCH_RADIUS_METERS} metros")
print()

# Limpar denúncias de teste anteriores
print("🧹 Limpando denúncias de teste...")
Denuncia.objects.filter(titulo__startswith="TESTE").delete()
print("   ✅ Denúncias de teste removidas")
print()

# Obter dados necessários
categoria_buraco = Categoria.objects.filter(nome__icontains="Buraco").first()
categoria_iluminacao = Categoria.objects.filter(nome__icontains="Iluminação").first()
estado = Estado.objects.first()
cidade = Cidade.objects.first()

if not all([categoria_buraco, categoria_iluminacao, estado, cidade]):
    print("❌ ERRO: Categorias, estados ou cidades não encontrados!")
    print("   Execute as migrações e popule o banco de dados.")
    exit(1)

print(f"📋 Dados de teste:")
print(f"   Categoria 1: {categoria_buraco.nome} (ID: {categoria_buraco.id})")
print(f"   Categoria 2: {categoria_iluminacao.nome} (ID: {categoria_iluminacao.id})")
print(f"   Estado: {estado.nome}")
print(f"   Cidade: {cidade.nome}")
print()

# Coordenadas de teste (Joinville, SC)
LAT_BASE = Decimal('-26.3045')
LON_BASE = Decimal('-48.8487')

# Coordenadas próximas (50m de distância)
LAT_PROXIMA = Decimal('-26.30495')  # ~50m ao sul
LON_PROXIMA = Decimal('-48.8487')

# Coordenadas distantes (200m de distância)
LAT_DISTANTE = Decimal('-26.3063')  # ~200m ao sul
LON_DISTANTE = Decimal('-48.8487')

# Verificar distâncias
dist_proxima = haversine_distance(LAT_BASE, LON_BASE, LAT_PROXIMA, LON_PROXIMA)
dist_distante = haversine_distance(LAT_BASE, LON_BASE, LAT_DISTANTE, LON_DISTANTE)

print(f"📍 Coordenadas de teste:")
print(f"   Base: {LAT_BASE}, {LON_BASE}")
print(f"   Próxima: {LAT_PROXIMA}, {LON_PROXIMA} ({dist_proxima:.2f}m)")
print(f"   Distante: {LAT_DISTANTE}, {LON_DISTANTE} ({dist_distante:.2f}m)")
print()

# ==========================================
# TESTE 1: Mesma categoria, dentro do raio
# ==========================================
print("=" * 80)
print("TESTE 1: Mesma categoria, dentro do raio (< 100m)")
print("=" * 80)

denuncia1 = Denuncia.objects.create(
    titulo="TESTE - Buraco Perigoso 1",
    descricao="Buraco de teste",
    autor_convidado="Teste Usuario 1",
    categoria=categoria_buraco,
    cidade=cidade,
    estado=estado,
    latitude=LAT_BASE,
    longitude=LON_BASE,
    jurisdicao=Denuncia.Jurisdicao.MUNICIPAL,
    foto="test.jpg"
)
print(f"✅ Denúncia 1 criada (ID: {denuncia1.id})")
print(f"   Categoria: {denuncia1.categoria.nome}")
print(f"   Coordenadas: {denuncia1.latitude}, {denuncia1.longitude}")
print(f"   Apoios iniciais: {denuncia1.apoios.count()}")

denuncia2_data = {
    'titulo': "TESTE - Buraco Perigoso 2",
    'descricao': "Buraco de teste próximo",
    'categoria': categoria_buraco,
    'cidade': cidade,
    'estado': estado,
    'latitude': LAT_PROXIMA,
    'longitude': LON_PROXIMA,
    'jurisdicao': Denuncia.Jurisdicao.MUNICIPAL,
    'foto': "test2.jpg"
}

# Simular criação via service
from applications.denuncias.services import criar_ou_apoiar_denuncia
denuncia_resultado, created, apoio_created = criar_ou_apoiar_denuncia(
    denuncia2_data,
    user=None,
    autor_convidado="Teste Usuario 2"
)

print()
print(f"📊 Resultado:")
if created:
    print(f"   ❌ FALHOU: Nova denúncia foi criada (ID: {denuncia_resultado.id})")
    print(f"   Esperado: Apoio na denúncia existente")
else:
    if apoio_created:
        print(f"   ✅ PASSOU: Apoio adicionado à denúncia {denuncia_resultado.id}")
        print(f"   Total de apoios: {denuncia_resultado.apoios.count()}")
    else:
        print(f"   ⚠️  Denúncia encontrada mas apoio não criado")

print()

# ==========================================
# TESTE 2: Categorias diferentes, dentro do raio
# ==========================================
print("=" * 80)
print("TESTE 2: Categorias diferentes, dentro do raio")
print("=" * 80)

denuncia3_data = {
    'titulo': "TESTE - Iluminação Quebrada",
    'descricao': "Poste apagado",
    'categoria': categoria_iluminacao,
    'cidade': cidade,
    'estado': estado,
    'latitude': LAT_PROXIMA,  # Mesma coordenada da tentativa anterior
    'longitude': LON_PROXIMA,
    'jurisdicao': Denuncia.Jurisdicao.MUNICIPAL,
    'foto': "test3.jpg"
}

denuncia_resultado, created, apoio_created = criar_ou_apoiar_denuncia(
    denuncia3_data,
    user=None,
    autor_convidado="Teste Usuario 3"
)

print()
print(f"📊 Resultado:")
if created:
    print(f"   ✅ PASSOU: Nova denúncia criada (ID: {denuncia_resultado.id})")
    print(f"   Categoria diferente não agrupou")
else:
    print(f"   ❌ FALHOU: Denúncia foi agrupada (categorias diferentes!)")

print()

# ==========================================
# TESTE 3: Mesma categoria, fora do raio (> 100m)
# ==========================================
print("=" * 80)
print("TESTE 3: Mesma categoria, fora do raio (> 100m)")
print("=" * 80)

denuncia4_data = {
    'titulo': "TESTE - Buraco Distante",
    'descricao': "Buraco longe",
    'categoria': categoria_buraco,
    'cidade': cidade,
    'estado': estado,
    'latitude': LAT_DISTANTE,
    'longitude': LON_DISTANTE,
    'jurisdicao': Denuncia.Jurisdicao.MUNICIPAL,
    'foto': "test4.jpg"
}

denuncia_resultado, created, apoio_created = criar_ou_apoiar_denuncia(
    denuncia4_data,
    user=None,
    autor_convidado="Teste Usuario 4"
)

print()
print(f"📊 Resultado:")
if created:
    print(f"   ✅ PASSOU: Nova denúncia criada (ID: {denuncia_resultado.id})")
    print(f"   Distância > 100m não agrupou")
else:
    print(f"   ❌ FALHOU: Denúncia foi agrupada (distância > 100m!)")

print()

# ==========================================
# TESTE 4: Denúncia resolvida não agrupa
# ==========================================
print("=" * 80)
print("TESTE 4: Denúncia resolvida não agrupa")
print("=" * 80)

# Marcar primeira denúncia como resolvida
denuncia1.status = Denuncia.Status.RESOLVIDA
denuncia1.save()
print(f"✅ Denúncia {denuncia1.id} marcada como RESOLVIDA")

denuncia5_data = {
    'titulo': "TESTE - Buraco no Local Resolvido",
    'descricao': "Buraco no mesmo local",
    'categoria': categoria_buraco,
    'cidade': cidade,
    'estado': estado,
    'latitude': LAT_BASE,  # Mesma coordenada da denúncia resolvida
    'longitude': LON_BASE,
    'jurisdicao': Denuncia.Jurisdicao.MUNICIPAL,
    'foto': "test5.jpg"
}

denuncia_resultado, created, apoio_created = criar_ou_apoiar_denuncia(
    denuncia5_data,
    user=None,
    autor_convidado="Teste Usuario 5"
)

print()
print(f"📊 Resultado:")
if created:
    print(f"   ✅ PASSOU: Nova denúncia criada (ID: {denuncia_resultado.id})")
    print(f"   Não agrupou com denúncia resolvida")
else:
    print(f"   ❌ FALHOU: Denúncia foi agrupada com denúncia resolvida!")

print()

# ==========================================
# RESUMO FINAL
# ==========================================
print("=" * 80)
print("📊 RESUMO DOS TESTES")
print("=" * 80)
print()

total_denuncias = Denuncia.objects.filter(titulo__startswith="TESTE").count()
total_apoios = ApoioDenuncia.objects.filter(denuncia__titulo__startswith="TESTE").count()

print(f"📈 Estatísticas:")
print(f"   Total de denúncias criadas: {total_denuncias}")
print(f"   Total de apoios registrados: {total_apoios}")
print()

print(f"📋 Denúncias criadas:")
for d in Denuncia.objects.filter(titulo__startswith="TESTE"):
    print(f"   ID: {d.id} | {d.titulo}")
    print(f"      Categoria: {d.categoria.nome}")
    print(f"      Status: {d.status}")
    print(f"      Apoios: {d.apoios.count()}")
    print()

print("=" * 80)
print("✅ TESTES CONCLUÍDOS!")
print("=" * 80)
print()
print("💡 Para limpar os dados de teste:")
print("   Denuncia.objects.filter(titulo__startswith='TESTE').delete()")
