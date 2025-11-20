# 📱 Instruções para o Flutter - Correções de Bugs

## 🐛 Problemas Corrigidos no Backend:

### ✅ 1. Endpoint "Minhas Denúncias"
Agora existem **2 formas** de buscar apenas as denúncias do usuário:

#### **Opção A - Query parameter (RECOMENDADO):**
```dart
// GET /api/denuncias/denuncias/?minhas=true
final response = await dio.get(
  'http://72.61.55.172:8000/api/denuncias/denuncias/',
  queryParameters: {'minhas': 'true'},
  options: Options(
    headers: {'Authorization': 'Bearer $token'},
  ),
);
```

#### **Opção B - Endpoint dedicado:**
```dart
// GET /api/denuncias/denuncias/minhas_denuncias/
final response = await dio.get(
  'http://72.61.55.172:8000/api/denuncias/denuncias/minhas_denuncias/',
  options: Options(
    headers: {'Authorization': 'Bearer $token'},
  ),
);
```

### ✅ 2. DELETE de Denúncia
O endpoint DELETE já existe e funciona:

```dart
// DELETE /api/denuncias/denuncias/{id}/
final response = await dio.delete(
  'http://72.61.55.172:8000/api/denuncias/denuncias/$denunciaId/',
  options: Options(
    headers: {'Authorization': 'Bearer $token'},
  ),
);

// Resposta de sucesso (200):
// {
//   "message": "Denúncia deletada com sucesso. X apoio(s) foram transferidos...",
//   "apoios_transferidos": 2,
//   "denuncia_destino_id": 123
// }
```

**Regras de DELETE:**
- ✅ Apenas o **autor** pode deletar sua denúncia
- ✅ Se tiver apoios, eles são **transferidos** para denúncia próxima
- ✅ Se não houver denúncia próxima, o **apoio mais antigo vira nova denúncia**
- ✅ Requer **autenticação** (token JWT)

### ✅ 3. Timeout aumentado
- Timeout do Gunicorn aumentado de **120s para 300s**
- Adicionado `graceful-timeout` de 300s
- Admin otimizado com `list_per_page = 50`

---

## 🗺️ Problemas que DEVEM ser resolvidos no Flutter:

### ❌ 1. Latitude/Longitude aparecendo ao invés do nome da cidade

**Causa:** O backend retorna `cidade` como objeto com ID, mas você provavelmente está exibindo o campo errado.

**Solução Flutter:**

```dart
// ❌ ERRADO - Isso retorna o ID
String localizacao = denuncia['cidade'].toString(); // "5275"

// ✅ CORRETO - Usar o endpoint de cidades para pegar o nome
// Opção 1: Incluir nome da cidade na resposta (fazer join no serializer)
// Opção 2: Buscar cidade separadamente
final cidadeResponse = await dio.get(
  'http://72.61.55.172:8000/api/localidades/cidades/${denuncia['cidade']}/',
);
String nomeCidade = cidadeResponse.data['nome']; // "São Paulo"

// Opção 3: Usar o campo 'endereco' que já vem preenchido
String localizacao = denuncia['endereco']; // "R. Br. de Itapetininga, República - São Paulo"
```

**Recomendação:** Use o campo `endereco` que já vem na resposta:
```dart
String localizacao = denuncia['endereco'] ?? 
                     '${denuncia['latitude']}, ${denuncia['longitude']}';
```

---

### ❌ 2. Mapa não centraliza na localização do usuário

**Solução Flutter:**

```dart
import 'package:geolocator/geolocator.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';

// Ao abrir o mapa:
Future<void> _centralizarNoUsuario() async {
  // Pedir permissão
  LocationPermission permission = await Geolocator.checkPermission();
  if (permission == LocationPermission.denied) {
    permission = await Geolocator.requestPermission();
  }
  
  if (permission == LocationPermission.deniedForever) {
    // Mostrar diálogo explicando que precisa de permissão
    return;
  }
  
  // Pegar localização atual
  Position position = await Geolocator.getCurrentPosition(
    desiredAccuracy: LocationAccuracy.high,
  );
  
  // Mover câmera do mapa
  final GoogleMapController controller = await _mapController.future;
  controller.animateCamera(
    CameraUpdate.newCameraPosition(
      CameraPosition(
        target: LatLng(position.latitude, position.longitude),
        zoom: 14.0,
      ),
    ),
  );
}

// Chamar no initState ou onMapCreated
@override
void initState() {
  super.initState();
  _centralizarNoUsuario();
}
```

---

### ❌ 3. Timeout na listagem de denúncias (10 segundos)

**Causa:** O servidor demora para carregar muitas denúncias (especialmente se tentar carregar imagens locais que não existem).

**Soluções Flutter:**

#### A) Aumentar timeout (solução temporária):
```dart
final dio = Dio(
  BaseOptions(
    baseUrl: 'http://72.61.55.172:8000',
    connectTimeout: Duration(seconds: 30),
    receiveTimeout: Duration(seconds: 30), // Aumentar de 10s para 30s
  ),
);
```

#### B) Paginação (solução definitiva):
```dart
// Usar paginação para carregar aos poucos
int currentPage = 1;
int pageSize = 10;

Future<void> carregarDenuncias() async {
  final response = await dio.get(
    '/api/denuncias/denuncias/',
    queryParameters: {
      'page': currentPage,
      'page_size': pageSize,
    },
  );
  
  // Adicionar ao lista existente
  List<dynamic> novasDenuncias = response.data['results'];
  denuncias.addAll(novasDenuncias);
  
  // Próxima página
  currentPage++;
}

// Implementar scroll infinito
class DenunciasListView extends StatefulWidget {
  @override
  _DenunciasListViewState createState() => _DenunciasListViewState();
}

class _DenunciasListViewState extends State<DenunciasListView> {
  ScrollController _scrollController = ScrollController();
  
  @override
  void initState() {
    super.initState();
    _scrollController.addListener(_onScroll);
    carregarDenuncias();
  }
  
  void _onScroll() {
    if (_scrollController.position.pixels >= 
        _scrollController.position.maxScrollExtent * 0.9) {
      // Carregar mais quando chegar a 90% do scroll
      carregarDenuncias();
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      controller: _scrollController,
      itemCount: denuncias.length,
      itemBuilder: (context, index) {
        return DenunciaCard(denuncia: denuncias[index]);
      },
    );
  }
}
```

#### C) **SOLUÇÃO DEFINITIVA: Aguardar Cloudinary estar funcionando**
Quando o Cloudinary estiver ativo, as imagens carregarão muito mais rápido do CDN.

---

## 🚀 Próximos Passos URGENTES:

### 1. **Ativar Cloudinary no Hostinger (PRIORIDADE MÁXIMA)**

No painel do Hostinger:

1. **Variáveis de Ambiente** → Adicionar:
   ```
   CLOUDINARY_URL=cloudinary://577511264787832:jxis6sQppAtWfpA35ttwyl4yxNQ@dphpzghkh
   ```

2. **Redesploy do container:**
   ```bash
   docker stop voz-do-povo-api
   docker rm voz-do-povo-api
   docker-compose up -d --build
   ```

3. **Verificar logs:**
   ```bash
   docker logs voz-do-povo-api --tail 50
   ```

4. **Testar criação de denúncia** - A URL da foto deve ser:
   ```
   https://res.cloudinary.com/dphpzghkh/image/upload/v.../denuncias_fotos/foto.jpg
   ```
   E NÃO:
   ```
   http://72.61.55.172:8000/media/denuncias_fotos/foto.jpg
   ```

---

### 2. **Atualizar código Flutter:**

#### A) Tela "Minhas Denúncias":
```dart
// Mudar de:
final response = await dio.get('/api/denuncias/denuncias/');

// Para:
final response = await dio.get(
  '/api/denuncias/denuncias/',
  queryParameters: {'minhas': 'true'},
  options: Options(
    headers: {'Authorization': 'Bearer $token'},
  ),
);
```

#### B) Exibir localização corretamente:
```dart
// Usar o campo 'endereco' que vem preenchido
Text(denuncia['endereco'] ?? 'Localização não disponível')
```

#### C) Implementar DELETE:
```dart
Future<void> deletarDenuncia(int id) async {
  try {
    final response = await dio.delete(
      '/api/denuncias/denuncias/$id/',
      options: Options(
        headers: {'Authorization': 'Bearer $token'},
      ),
    );
    
    if (response.statusCode == 200) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(response.data['message'])),
      );
      // Remover da lista local
      setState(() {
        denuncias.removeWhere((d) => d['id'] == id);
      });
    }
  } on DioException catch (e) {
    if (e.response?.statusCode == 403) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Você não tem permissão para deletar esta denúncia')),
      );
    }
  }
}
```

#### D) Centralizar mapa no usuário:
```dart
// Ver código completo acima na seção "Mapa não centraliza"
await _centralizarNoUsuario();
```

---

## 📊 Resumo das Mudanças:

### Backend (Django) - ✅ FEITO:
- [x] Endpoint `?minhas=true` para filtrar denúncias do usuário
- [x] Action `minhas_denuncias/` dedicada
- [x] DELETE funciona com transferência de apoios
- [x] Timeout aumentado para 300s
- [x] Admin otimizado (50 itens por página)
- [x] Volume `media_volume` removido (não mais necessário com Cloudinary)

### Frontend (Flutter) - ❌ PENDENTE:
- [ ] Usar `?minhas=true` na tela "Minhas Denúncias"
- [ ] Exibir `endereco` ao invés de lat/lng
- [ ] Centralizar mapa na localização do usuário
- [ ] Implementar botão DELETE com confirmação
- [ ] Aumentar timeout do Dio para 30s
- [ ] Implementar paginação/scroll infinito

### Infraestrutura - ❌ URGENTE:
- [ ] Adicionar `CLOUDINARY_URL` no Hostinger
- [ ] Redesploy do container
- [ ] Testar upload de foto → deve ir para Cloudinary
- [ ] Verificar performance (não deve mais ter timeout)

---

## 🔍 Como testar se tudo está funcionando:

1. **Minhas Denúncias:**
   ```bash
   curl -H "Authorization: Bearer SEU_TOKEN" \
        "http://72.61.55.172:8000/api/denuncias/denuncias/?minhas=true"
   ```
   Deve retornar APENAS as denúncias do usuário do token.

2. **Cloudinary ativo:**
   Criar denúncia e verificar que `foto` contém:
   ```
   https://res.cloudinary.com/dphpzghkh/...
   ```

3. **DELETE funciona:**
   ```bash
   curl -X DELETE \
        -H "Authorization: Bearer SEU_TOKEN" \
        "http://72.61.55.172:8000/api/denuncias/denuncias/123/"
   ```
   Deve retornar 200 com mensagem de sucesso.

---

**🎯 PRIORIDADE: Ativar Cloudinary no Hostinger AGORA!**

Isso vai resolver:
- ✅ Timeout de 10 segundos
- ✅ Worker timeout no admin
- ✅ Performance geral do app
- ✅ Escalabilidade (armazenamento ilimitado)
