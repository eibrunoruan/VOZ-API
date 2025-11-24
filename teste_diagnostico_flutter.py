"""
Script de diagnóstico para identificar por que o Flutter recebe erro 500
mas o RequestFactory funciona.

Execute no VPS:
docker exec -it voz-do-povo-api python manage.py shell < teste_diagnostico_flutter.py
"""

print("\n" + "="*80)
print("TESTE DIAGNÓSTICO - REQUISIÇÃO EXATAMENTE COMO FLUTTER ENVIA")
print("="*80 + "\n")

from django.test import RequestFactory
from applications.denuncias.views import DenunciaViewSet
from PIL import Image
from io import BytesIO
import traceback
from django.contrib.auth.models import AnonymousUser
import json

# Criar RequestFactory
factory = RequestFactory()

# Criar imagem de teste (mesma do Flutter)
img = Image.new('RGB', (100, 100), color='red')
img_io = BytesIO()
img.save(img_io, format='JPEG', quality=70)
img_io.seek(0)
img_io.name = 'compressed_test.jpg'

print("📦 DADOS QUE O FLUTTER ENVIA:")
print("-" * 80)

# Dados EXATAMENTE como o Flutter envia
post_data = {
    'titulo': 'dasfasf',
    'descricao': 'safasfasf',
    'categoria': '6',
    'cidade': '5275',
    'estado': '25',
    'latitude': '-23.549241',
    'longitude': '-46.631583',
    'jurisdicao': 'MUNICIPAL',
    'endereco': 'R. Venceslau Brás, Centro Histórico de São Paulo - São Paulo',
    'autor_convidado': 'okok',
    'foto': img_io
}

for key, value in post_data.items():
    if key != 'foto':
        print(f"   {key}: {value} (tipo: {type(value).__name__})")
    else:
        print(f"   foto: {img_io.name} (tamanho: {len(img_io.getvalue())} bytes)")

print("\n🔄 PROCESSANDO REQUISIÇÃO...")
print("-" * 80)

try:
    # Criar requisição POST multipart
    request = factory.post(
        '/api/denuncias/denuncias/',
        data=post_data,
        format='multipart'
    )
    
    # Simular usuário guest (AnonymousUser)
    request.user = AnonymousUser()
    
    print(f"✅ Request criado:")
    print(f"   method: {request.method}")
    print(f"   path: {request.path}")
    print(f"   user: {request.user}")
    print(f"   user.is_authenticated: {request.user.is_authenticated}")
    print(f"   content_type: {request.content_type}")
    
    print(f"\n📋 POST data recebido pelo Django:")
    for key in request.POST.keys():
        print(f"   {key}: {request.POST.get(key)}")
    
    print(f"\n📸 FILES recebidos:")
    for key in request.FILES.keys():
        file_obj = request.FILES.get(key)
        print(f"   {key}: {file_obj.name} ({file_obj.size} bytes, {file_obj.content_type})")
    
    print("\n🔍 EXECUTANDO VIEW...")
    print("-" * 80)
    
    # Executar view
    view = DenunciaViewSet.as_view({'post': 'create'})
    response = view(request)
    
    print(f"\n✅ RESPOSTA DO BACKEND:")
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code == 201:
        print("   ✅ SUCESSO! Denúncia criada")
        print(f"\n📦 Response Data:")
        for key, value in response.data.items():
            if key == 'foto':
                print(f"   {key}: {value}")
            else:
                print(f"   {key}: {value}")
    else:
        print(f"   ❌ ERRO! Status {response.status_code}")
        print(f"\n📦 Response Data:")
        print(f"   {response.data}")
        
except Exception as e:
    print(f"\n❌ EXCEÇÃO CAPTURADA:")
    print(f"   Tipo: {type(e).__name__}")
    print(f"   Mensagem: {str(e)}")
    print(f"\n🔍 STACK TRACE COMPLETO:")
    print("-" * 80)
    traceback.print_exc()
    print("-" * 80)

print("\n" + "="*80)
print("FIM DO TESTE DIAGNÓSTICO")
print("="*80 + "\n")

print("\n🎯 PRÓXIMOS PASSOS:")
print("1. Se status 201: backend funciona, problema é em como Flutter monta a requisição HTTP")
print("2. Se status 400: problema de validação (ver response.data)")
print("3. Se exceção: problema no código Django (ver stack trace)")
print("4. Se status 500: erro interno não capturado (ativar DEBUG=True)")
