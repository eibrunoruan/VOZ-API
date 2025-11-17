import requests

# Testar API do IBGE para São Paulo
response = requests.get('https://servicodados.ibge.gov.br/api/v1/localidades/estados/SP/municipios')
cidades = response.json()

print(f'Total de municípios retornados pela API do IBGE: {len(cidades)}\n')

# Procurar especificamente São Paulo
sp_encontrada = False
for cidade in cidades:
    if 'São Paulo' in cidade['nome']:
        print(f"✅ Encontrado: {cidade['nome']} (ID IBGE: {cidade['id']})")
        sp_encontrada = True
        
if not sp_encontrada:
    print('❌ Cidade "São Paulo" NÃO encontrada na API do IBGE')
    print('\nPrimeiros 10 municípios:')
    for cidade in cidades[:10]:
        print(f'  - {cidade["nome"]}')
