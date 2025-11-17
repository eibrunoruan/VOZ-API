import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'voz_do_povo.settings')
django.setup()

from applications.localidades.models import Cidade, Estado

# Verificar estado de São Paulo
sp = Estado.objects.get(uf='SP')
print(f'Estado: {sp.nome}')
print(f'Total de cidades cadastradas em SP: {sp.cidades.count()}')

# Procurar cidade de São Paulo
sp_cidade = sp.cidades.filter(nome__iexact='São Paulo').first()
print(f'\nCidade "São Paulo" existe no banco: {sp_cidade is not None}')

if sp_cidade:
    print(f'ID: {sp_cidade.id}, Nome: {sp_cidade.nome}')
else:
    print('\n❌ A cidade de São Paulo NÃO está cadastrada!')
    print('\nPrimeiras 10 cidades cadastradas em SP:')
    for cidade in sp.cidades.all()[:10]:
        print(f'  - {cidade.nome}')
