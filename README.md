# Voz do Povo - Backend

Este é o backend para o projeto Voz do Povo, uma plataforma para conectar cidadãos e a gestão pública.

## O Que Foi Feito

1.  **Modelo de Usuário Customizado**: Foi implementado um modelo de usuário (`User`) customizado que herda do `AbstractUser` do Django. Isso permite maior flexibilidade para futuras modificações.
2.  **Gerenciador de Usuário**: Um `UserManager` customizado foi criado para gerenciar a criação de usuários e superusuários, utilizando `email` e `username` como campos principais.
3.  **Ajuste no Campo `username`**: O modelo `User` e seu gerenciador foram ajustados para resolver um `TypeError` que ocorria durante a criação de um superusuário. O campo `username` foi definido como o campo de login (`USERNAME_FIELD`).
4.  **Estrutura de Autenticação**: Foram criadas as rotas e views básicas para registro (`/api/auth/register/`) e login (`/api/auth/login/`) de usuários usando `djangorestframework-simplejwt` para autenticação baseada em token.
5.  **API de Localidades**: Foi criada a API para consulta de estados e cidades, com rotas em `/api/localidades/`. Os dados de estados são populados via migração e os de cidades através de um comando customizado que consome a API do IBGE.

## Como Rodar o Projeto

1.  **Clone o Repositório** (se ainda não o fez).

2.  **Crie e Ative um Ambiente Virtual**:
    ```bash
    # Crie o ambiente virtual
    python -m venv .venv

    # Ative no Windows
    .\.venv\Scripts\activate

    # Ative no Linux/macOS
    # source .venv/bin/activate
    ```

3.  **Instale as Dependências**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Execute as Migrações do Banco de Dados**:
    ```bash
    python manage.py migrate
    ```

5.  **Popule o Banco de Dados com Localidades**:
    Execute os comandos abaixo para popular o banco de dados com os estados e cidades do Brasil.
    ```bash
    # Popula os estados (executa a migração de dados)
    python manage.py migrate localidades

    # Popula as cidades (executa o comando customizado)
    python manage.py populate_cities
    ```

6.  **Crie um Superusuário** (para acesso ao Admin):
    ```bash
    python manage.py createsuperuser
    ```
    Siga as instruções no terminal para definir `username`, `email` e `password`.

7.  **Inicie o Servidor de Desenvolvimento**:
    
    **Para uso com app Flutter (recomendado):**
    ```bash
    python manage.py runserver 0.0.0.0:8000
    ```
    
    **Ou use os scripts automatizados:**
    - Windows: Duplo clique em `start_server.bat`
    - PowerShell: `.\start_server.ps1` (com diagnóstico)
    
    O servidor estará disponível em `http://0.0.0.0:8000/`.

## Rotas da API

Aqui estão as rotas de autenticação disponíveis e como interagir com elas.

---

### Registro de Usuário

-   **Endpoint**: `POST /api/auth/register/`
-   **Descrição**: Cria um novo usuário no sistema.
-   **Body (raw/json)**:
    ```json
    {
        "username": "seu_username",
        "email": "seu_email@exemplo.com",
        "password": "sua_senha_forte",
        "first_name": "Seu Nome"
    }
    ```
-   **Resposta de Sucesso (201 Created)**:
    ```json
    {
        "id": 1,
        "username": "seu_username",
        "email": "seu_email@exemplo.com",
        "first_name": "Seu Nome"
    }
    ```

---

### Login de Usuário

-   **Endpoint**: `POST /api/auth/login/`
-   **Descrição**: Autentica um usuário e retorna um par de tokens JWT (acesso e atualização).
-   **Body (raw/json)**:
    ```json
    {
        "username": "seu_username",
        "password": "sua_senha_forte"
    }
    ```
-   **Resposta de Sucesso (200 OK)**:
    ```json
    {
        "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
    ```

---

### Atualizar Token de Acesso

-   **Endpoint**: `POST /api/auth/login/refresh/`
-   **Descrição**: Gera um novo token de acesso usando um token de atualização (`refresh token`) válido.
-   **Body (raw/json)**:
    ```json
    {
        "refresh": "seu_refresh_token_obtido_no_login"
    }
    ```
-   **Resposta de Sucesso (200 OK)**:
    ```json
    {
        "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
    ```

---

### Localidades (`/api/localidades/`)

-   `GET /api/localidades/estados/`: Retorna uma lista de todos os estados do Brasil.
-   `GET /api/localidades/estados/{id}/`: Retorna os detalhes de um estado específico.
-   `GET /api/localidades/cidades/`: Retorna uma lista de cidades. Pode ser filtrado por estado.
-   `GET /api/localidades/cidades/{id}/`: Retorna os detalhes de uma cidade específica.

---

## Configuração para App Flutter

### Permitir Conexões Externas

Para que o app Flutter no celular possa se conectar ao backend:

1. **Configure o ALLOWED_HOSTS** (já configurado):
   - O arquivo `settings.py` já inclui seu IP local
   - Inclui `*` para aceitar qualquer host em desenvolvimento

2. **Inicie o servidor corretamente**:
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```
   ⚠️ Use `0.0.0.0:8000` (não apenas `8000` ou `localhost`)

3. **Configure o Firewall do Windows**:
   ```powershell
   # Execute como Administrador
   New-NetFirewallRule -DisplayName "Django Dev Server" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
   ```

4. **Descubra seu IP local**:
   ```powershell
   ipconfig | findstr "IPv4"
   ```
   Anote o IP que começa com `192.168.x.x`

5. **Configure o Flutter**:
   No app Flutter, use: `http://SEU_IP:8000`
   Exemplo: `http://192.168.1.10:8000`

### Testes

**No navegador do PC:**
- http://localhost:8000/api/denuncias/denuncias/

**No navegador do celular (mesma rede Wi-Fi):**
- http://192.168.1.10:8000/api/denuncias/denuncias/

Se funcionar no navegador do celular, o app Flutter também funcionará.

---

## Informações Importantes para Desenvolvimento

### Valores para Criar Denúncias

**Jurisdição** (String, maiúsculas):
- `'MUNICIPAL'`, `'ESTADUAL'`, `'FEDERAL'`, `'PRIVADO'`

**Categorias** (Integer):
- 1: Iluminação Pública
- 2: Saneamento Básico
- 3: Buracos na Via
- 4: Lixo Acumulado
- 5: Transporte Público
- 6: Segurança Pública
- 7: Manutenção de Praças e Parques
- 8: Poluição Sonora
- 9: Controle de Pragas Urbanas
- 10: Acessibilidade
- 11: Outros

**Estados** (Integer):
- Consulte: `GET /api/localidades/estados/`
- Exemplo SC: ID 24

**Cidades** (Integer):
- Consulte: `GET /api/localidades/cidades/?estado=24`
- Exemplo Joinville: ID 4554

### Sistema de Agrupamento de Denúncias

O backend agrupa denúncias automaticamente quando:
- ✅ Mesma categoria
- ✅ Distância < 100 metros
- ✅ Status não resolvido

Quando uma denúncia é agrupada, cria-se um "apoio" à denúncia existente.

**Resposta ao criar denúncia:**
```json
// Nova denúncia criada (201 Created)
{
  "id": 123,
  "titulo": "...",
  "total_apoios": 0
}

// Apoio adicionado (200 OK)
{
  "message": "Denúncia similar encontrada próxima. Seu apoio foi registrado!",
  "apoio_adicionado": true,
  "denuncia": {
    "id": 123,
    "total_apoios": 2
  }
}
```

---

## Troubleshooting

### Backend não inicia

**Erro: "ModuleNotFoundError"**
```bash
pip install -r requirements.txt
```

**Erro: "Port already in use"**
```powershell
netstat -ano | findstr :8000
taskkill /PID <numero_do_pid> /F
```

### Celular não conecta

1. Verifique se PC e celular estão na mesma rede Wi-Fi
2. Teste no navegador do celular primeiro
3. Verifique o firewall (veja seção "Configuração para App Flutter")
4. Confirme que está usando `0.0.0.0:8000`

### IP mudou

Quando reiniciar o roteador, o IP pode mudar. Execute:
```powershell
ipconfig | findstr "IPv4"
```
E atualize no Flutter e no `ALLOWED_HOSTS` se necessário.

---

## Arquivos Úteis

- **rotas.md**: Documentação completa de todas as rotas da API
- **GEMINI.md**: Instruções e contexto do projeto para o Copilot
- **start_server.bat / .ps1**: Scripts para iniciar o servidor automaticamente

---

## Suporte

Para mais detalhes sobre as rotas da API, consulte o arquivo `rotas.md`.
