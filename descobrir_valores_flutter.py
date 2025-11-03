#!/usr/bin/env python
"""
Script para descobrir os valores corretos para o Flutter
Executar: python descobrir_valores_flutter.py
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'voz_do_povo.settings')
django.setup()

from applications.denuncias.models import Denuncia, Categoria
from applications.localidades.models import Estado, Cidade

print("=" * 80)
print("📋 INFORMAÇÕES PARA O FLUTTER - VOZ DO POVO")
print("=" * 80)
print()

# 1. JURISDIÇÃO
print("=" * 80)
print("1️⃣  JURISDIÇÃO (campo 'jurisdicao')")
print("=" * 80)
print()
print("✅ Valores aceitos pelo backend:")
for choice_value, choice_label in Denuncia.Jurisdicao.choices:
    print(f"   - '{choice_value}' → {choice_label}")
print()
print("💡 Use no Flutter: 'MUNICIPAL', 'ESTADUAL', 'FEDERAL', ou 'PRIVADO'")
print()

# 2. STATUS (informacional)
print("=" * 80)
print("2️⃣  STATUS (campo 'status' - opcional, tem default)")
print("=" * 80)
print()
print("✅ Valores aceitos:")
for choice_value, choice_label in Denuncia.Status.choices:
    print(f"   - '{choice_value}' → {choice_label}")
print()
print("💡 Default: 'ABERTA' (não precisa enviar)")
print()

# 3. CATEGORIAS
print("=" * 80)
print("3️⃣  CATEGORIAS (campo 'categoria')")
print("=" * 80)
print()
categorias = Categoria.objects.all()
if categorias.exists():
    print(f"✅ {categorias.count()} categorias cadastradas:")
    print()
    for cat in categorias:
        print(f"   ID: {cat.id:3d} | Nome: {cat.nome}")
    print()
    print(f"💡 Use no Flutter: categoria: {categorias.first().id} (ID da categoria)")
else:
    print("❌ NENHUMA CATEGORIA CADASTRADA!")
    print("   Execute: python manage.py loaddata categorias.json")
    print("   Ou crie categorias manualmente no admin")
print()

# 4. ESTADOS
print("=" * 80)
print("4️⃣  ESTADOS (campo 'estado')")
print("=" * 80)
print()
estados = Estado.objects.all()
if estados.exists():
    print(f"✅ {estados.count()} estados cadastrados:")
    print()
    # Mostrar alguns importantes
    estados_importantes = ['SC', 'SP', 'RJ', 'MG', 'GO', 'PR', 'RS']
    for sigla in estados_importantes:
        estado = estados.filter(sigla=sigla).first()
        if estado:
            print(f"   ID: {estado.id:2d} | Sigla: {estado.sigla} | Nome: {estado.nome}")
    
    # Mostrar todos se forem poucos
    if estados.count() <= 10:
        print()
        print("   Todos os estados:")
        for estado in estados:
            print(f"   ID: {estado.id:2d} | Sigla: {estado.sigla} | Nome: {estado.nome}")
    
    print()
    print(f"💡 Use no Flutter: estado: {estados.first().id} (ID do estado)")
else:
    print("❌ NENHUM ESTADO CADASTRADO!")
    print("   Execute: python manage.py migrate")
    print("   A migração 0002_popular_estados deve popular automaticamente")
print()

# 5. CIDADES (exemplo Santa Catarina)
print("=" * 80)
print("5️⃣  CIDADES (campo 'cidade')")
print("=" * 80)
print()
sc = Estado.objects.filter(sigla='SC').first()
if sc:
    cidades_sc = Cidade.objects.filter(estado=sc).order_by('nome')
    if cidades_sc.exists():
        print(f"✅ {cidades_sc.count()} cidades cadastradas em Santa Catarina")
        print()
        print("   Primeiras 20 cidades:")
        for cidade in cidades_sc[:20]:
            print(f"   ID: {cidade.id:7d} | Nome: {cidade.nome}")
        
        # Procurar cidades específicas
        print()
        print("   Cidades importantes de SC:")
        cidades_importantes = ['Joinville', 'Florianópolis', 'Blumenau', 'Chapecó', 'Itajaí']
        for nome in cidades_importantes:
            cidade = cidades_sc.filter(nome__iexact=nome).first()
            if cidade:
                print(f"   ID: {cidade.id:7d} | Nome: {cidade.nome}")
        
        print()
        print(f"💡 Use no Flutter: cidade: {cidades_sc.first().id} (ID da cidade)")
    else:
        print("❌ NENHUMA CIDADE CADASTRADA EM SC!")
        print("   Execute: python manage.py populate_cities")
else:
    print("⚠️  Estado SC não encontrado")
    
    # Tentar qualquer estado
    if estados.exists():
        primeiro_estado = estados.first()
        print(f"   Usando {primeiro_estado.nome} como exemplo...")
        cidades = Cidade.objects.filter(estado=primeiro_estado)[:10]
        if cidades.exists():
            print()
            print(f"   Primeiras cidades de {primeiro_estado.nome}:")
            for cidade in cidades:
                print(f"   ID: {cidade.id:7d} | Nome: {cidade.nome}")
            print()
            print(f"💡 Use no Flutter: cidade: {cidades.first().id}, estado: {primeiro_estado.id}")
        else:
            print()
            print("❌ NENHUMA CIDADE CADASTRADA!")
            print("   Execute: python manage.py populate_cities")
print()

# 6. RESUMO FINAL
print("=" * 80)
print("📝 RESUMO - COPIE ESTES VALORES PARA O FLUTTER")
print("=" * 80)
print()

# Pegar valores reais
exemplo_categoria = categorias.first() if categorias.exists() else None
exemplo_estado = estados.first() if estados.exists() else None
exemplo_cidade = None

if exemplo_estado:
    exemplo_cidade = Cidade.objects.filter(estado=exemplo_estado).first()

print("Map<String, dynamic> denunciaData = {{")
print(f"  'titulo': 'Teste de Denúncia',")
print(f"  'descricao': 'Descrição da denúncia',")
print(f"  'autor_convidado': 'Nome do Usuário',")
print(f"  'categoria': {exemplo_categoria.id if exemplo_categoria else '1'},  // {exemplo_categoria.nome if exemplo_categoria else 'CRIAR CATEGORIA NO ADMIN!'}")
print(f"  'cidade': {exemplo_cidade.id if exemplo_cidade else '1'},  // {exemplo_cidade.nome if exemplo_cidade else 'POPULAR CIDADES!'}")
print(f"  'estado': {exemplo_estado.id if exemplo_estado else '1'},  // {exemplo_estado.sigla if exemplo_estado else 'POPULAR ESTADOS!'}")
print(f"  'latitude': -26.3051,")
print(f"  'longitude': -48.8461,")
print(f"  'jurisdicao': 'MUNICIPAL',  // Opções: MUNICIPAL, ESTADUAL, FEDERAL, PRIVADO")
print(f"  'foto': <arquivo_imagem>,")
print("}};")
print()

# Avisos importantes
print("=" * 80)
print("⚠️  AVISOS IMPORTANTES")
print("=" * 80)
print()

if not categorias.exists():
    print("❌ CRIAR CATEGORIAS:")
    print("   1. Acesse: http://localhost:8000/admin/")
    print("   2. Login com superusuário")
    print("   3. Adicione categorias (ex: Iluminação, Saneamento, Infraestrutura)")
    print()

if not estados.exists():
    print("❌ POPULAR ESTADOS:")
    print("   python manage.py migrate")
    print()

if not Cidade.objects.exists():
    print("❌ POPULAR CIDADES:")
    print("   python manage.py populate_cities")
    print()

print("=" * 80)
print("✅ SCRIPT CONCLUÍDO!")
print("=" * 80)
