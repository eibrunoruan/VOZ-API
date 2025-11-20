# 📋 DETALHAMENTO - Integração Cloudinary CDN

## 🎯 O que foi implementado no Backend (Django)

### 1. Pacotes Instalados
```bash
pip install cloudinary django-cloudinary-storage
```

Adicionados ao `requirements.txt`:
- `cloudinary==1.44.1`
- `django-cloudinary-storage==0.3.0`

### 2. Configuração do Django (`voz_do_povo/settings.py`)

#### Import necessário:
```python
import cloudinary
```

#### INSTALLED_APPS (ordem importa!):
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'cloudinary_storage',  # ANTES de 'cloudinary'
    'cloudinary',
    
    # ... suas apps
]
```

#### Configuração do Storage:
```python
# Inicialização do Cloudinary
cloudinary_url = config('CLOUDINARY_URL')
cloudinary.config(cloudinary_url=cloudinary_url)

# Configuração do Storage padrão
MEDIA_URL = '/media/'
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
```

#### Variável de Ambiente necessária:
```env
CLOUDINARY_URL=cloudinary://577511264787832:jxis6sQppAtWfpA35ttwyl4yxNQ@dphpzghkh
```

### 3. Como funciona automaticamente

O modelo `Denuncia` já tem o campo:
```python
foto = models.ImageField(upload_to='denuncias_fotos/', blank=False, null=False)
```

Com `DEFAULT_FILE_STORAGE` configurado, **AUTOMATICAMENTE**:
- Quando o Django recebe um arquivo no campo `foto`
- O `django-cloudinary-storage` intercepta o salvamento
- Envia a imagem para o Cloudinary CDN
- Salva a URL completa do CDN no banco de dados
- Retorna a URL do CDN na resposta da API

**Exemplo de URL retornada:**
```
https://res.cloudinary.com/dphpzghkh/image/upload/v1732123456/denuncias_fotos/foto_abc123.jpg
```

---

## 🔄 O que NÃO precisa mudar no Flutter

✅ **O Flutter NÃO precisa de nenhuma alteração** se já está enviando corretamente!

O código atual que você tem deve continuar funcionando **desde que**:

1. Esteja enviando como `multipart/form-data`
2. O campo da imagem se chame `foto` (igual ao model Django)
3. Esteja enviando para o endpoint correto: `POST /api/denuncias/denuncias/`

---

## 🚨 IMPORTANTE: O que pode estar causando o erro

### Problema Identificado:
Você mencionou que está **"salvando localmente ainda no App"**. Isso sugere que:

❌ **O Flutter está enviando um PATH local** (ex: `/storage/emulated/0/Pictures/foto.jpg`)
❌ **Ao invés de enviar o ARQUIVO em si**

### ✅ Como deve ser feito no Flutter:

```dart
// ❌ ERRADO - Enviar apenas o path
FormData formData = FormData.fromMap({
  'foto': '/storage/emulated/0/Pictures/foto.jpg', // String path
  'titulo': 'Buraco na rua',
  // ... outros campos
});

// ✅ CORRETO - Enviar o arquivo usando MultipartFile
FormData formData = FormData.fromMap({
  'foto': await MultipartFile.fromFile(
    imagePath,  // Path local da imagem
    filename: 'foto.jpg',
    contentType: MediaType('image', 'jpeg'),
  ),
  'titulo': 'Buraco na rua',
  'descricao': 'Descrição...',
  'categoria': 1,
  'cidade': 123,
  'estado': 1,
  'latitude': -23.5505,
  'longitude': -46.6333,
  'jurisdicao': 'MUNICIPAL',
  'autor_convidado': 'Nome do Usuário', // Se não autenticado
});

// Enviar
final response = await dio.post(
  'http://72.61.55.172:8000/api/denuncias/denuncias/',
  data: formData,
);
```

### 📦 Imports necessários no Flutter:

```dart
import 'package:dio/dio.dart';
import 'package:http_parser/http_parser.dart';
```

---

## 🔍 Verificação - Como o Backend espera receber

O Django DRF espera receber no formato `multipart/form-data` com:

```http
POST /api/denuncias/denuncias/ HTTP/1.1
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary...

------WebKitFormBoundary...
Content-Disposition: form-data; name="foto"; filename="foto.jpg"
Content-Type: image/jpeg

[BINARY DATA DA IMAGEM AQUI]
------WebKitFormBoundary...
Content-Disposition: form-data; name="titulo"

Buraco na rua
------WebKitFormBoundary...
Content-Disposition: form-data; name="descricao"

Buraco grande...
------WebKitFormBoundary...
```

**IMPORTANTE:** 
- ✅ O campo `foto` deve conter os **bytes da imagem**
- ❌ NÃO pode ser apenas uma string com o path local

---

## 🧪 Como testar se está funcionando

### 1. Teste via API (Postman/Insomnia)

```http
POST http://72.61.55.172:8000/api/denuncias/denuncias/
Content-Type: multipart/form-data

foto: [SELECIONAR ARQUIVO]
titulo: "Teste CDN"
descricao: "Testando Cloudinary"
categoria: 1
cidade: 4493
estado: 25
latitude: -23.5505
longitude: -46.6333
jurisdicao: "MUNICIPAL"
autor_convidado: "Teste"
```

### 2. Verifique a resposta JSON

A resposta deve conter a URL do Cloudinary:

```json
{
  "id": 123,
  "titulo": "Teste CDN",
  "descricao": "Testando Cloudinary",
  "foto": "https://res.cloudinary.com/dphpzghkh/image/upload/v1732123456/denuncias_fotos/foto_abc.jpg",
  "autor": null,
  "autor_convidado": "Teste",
  "categoria": 1,
  "cidade": 4493,
  "estado": 25,
  "latitude": "-23.55050000",
  "longitude": "-46.63330000",
  "jurisdicao": "MUNICIPAL",
  "status": "ABERTA",
  "data_criacao": "2025-11-20T16:45:00Z",
  "total_apoios": 0
}
```

### 3. Verifique no Cloudinary Dashboard

Acesse: https://console.cloudinary.com/

- Login com as credenciais do Cloudinary
- Vá em **Media Library**
- Procure pela pasta `denuncias_fotos/`
- A imagem deve aparecer lá!

---

## 🐛 Debugging - Se ainda não funcionar

### 1. Verifique os logs do container no Hostinger

```bash
docker logs voz-do-povo-api
```

Procure por erros relacionados a:
- `ModuleNotFoundError: No module named 'cloudinary'`
- `KeyError: 'CLOUDINARY_URL'`
- `cloudinary.exceptions.*`

### 2. Verifique se a variável de ambiente está configurada

No container:
```bash
docker exec -it voz-do-povo-api env | grep CLOUDINARY
```

Deve retornar:
```
CLOUDINARY_URL=cloudinary://577511264787832:jxis6sQppAtWfpA35ttwyl4yxNQ@dphpzghkh
```

### 3. Teste manualmente no shell do Django

```bash
docker exec -it voz-do-povo-api python manage.py shell
```

```python
import cloudinary
print(cloudinary.config())
# Deve mostrar: cloud_name='dphpzghkh', api_key='577511264787832', ...
```

---

## 📝 Checklist de Deploy

No Hostinger:

- [ ] Variável `CLOUDINARY_URL` adicionada nas variáveis de ambiente
- [ ] Container redesployado (rebuild) para puxar código atualizado do GitHub
- [ ] `requirements.txt` atualizado com `cloudinary` e `django-cloudinary-storage`
- [ ] Container reiniciado após adicionar variável de ambiente

No Flutter:

- [ ] Verificar que está usando `MultipartFile.fromFile()` e não apenas string path
- [ ] Verificar que o campo se chama `foto` (igual ao model Django)
- [ ] Verificar que está enviando para `POST /api/denuncias/denuncias/`
- [ ] Verificar Content-Type: `multipart/form-data`

---

## 🎯 Resumo Final

**O que foi feito:**
1. Instalado `cloudinary` e `django-cloudinary-storage`
2. Configurado `DEFAULT_FILE_STORAGE` para usar Cloudinary
3. Adicionado `import cloudinary` e `cloudinary.config()`
4. Configurado variável `CLOUDINARY_URL`

**Como funciona:**
- O Flutter envia a imagem via `multipart/form-data`
- O Django recebe e automaticamente envia para o Cloudinary
- A URL do CDN é salva no banco
- A API retorna a URL do CDN para o Flutter exibir

**Próximo passo:**
- Verificar código Flutter para garantir que está enviando o **arquivo** e não apenas o **path**
- Se necessário, compartilhe o código Flutter de criação de denúncia para análise detalhada
