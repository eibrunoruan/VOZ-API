## Features Implementadas

- Sistema de Autenticação de Usuários
- API de Localidades (Estados e Cidades)
- Análise de Geolocalização
- Sistema de Gerenciamento de Denúncias
- Portal de Gestão Pública com Dashboard Analítico

# Documentação Completa das Rotas da API "Voz do Povo"

Este documento detalha todos os endpoints da API, incluindo os métodos HTTP, os corpos de requisição (body) esperados e uma breve descrição da funcionalidade.

---

## 1. Autenticação (`/api/auth/`)

Rotas para gerenciamento de usuários, incluindo registro, login e recuperação de senha.

### Registro de Novo Usuário
- **Método:** `POST`
- **Endpoint:** `/api/auth/register/`
- **Descrição:** Cria um novo usuário. A conta é criada como inativa e um e-mail de verificação é enviado.
- **Body (raw/json):**
  ```json
  {
      "username": "seu_username",
      "email": "seu_email@exemplo.com",
      "password": "sua_senha_forte",
      "first_name": "Seu Nome"
  }
  ```

### Verificação de E-mail
- **Método:** `POST`
- **Endpoint:** `/api/auth/verify-email/`
- **Descrição:** Ativa a conta do usuário usando o código de verificação enviado por e-mail.
- **Body (raw/json):**
  ```json
  {
      "email": "seu_email@exemplo.com",
      "code": "12345"
  }
  ```

### Login de Usuário
- **Método:** `POST`
- **Endpoint:** `/api/auth/login/`
- **Descrição:** Autentica um usuário com e-mail verificado e retorna um par de tokens JWT (acesso e atualização).
- **Body (raw/json):**
  ```json
  {
      "username": "seu_username",
      "password": "sua_senha_forte"
  }
  ```

### Atualizar Token de Acesso
- **Método:** `POST`
- **Endpoint:** `/api/auth/login/refresh/`
- **Descrição:** Gera um novo token de acesso usando um `refresh token` válido.
- **Body (raw/json):**
  ```json
  {
      "refresh": "seu_refresh_token_obtido_no_login"
  }
  ```

### Solicitar Redefinição de Senha
- **Método:** `POST`
- **Endpoint:** `/api/auth/password-reset/request/`
- **Descrição:** Inicia o fluxo de redefinição de senha. Envia um código de verificação para o e-mail do usuário, se ele existir.
- **Body (raw/json):**
  ```json
  {
      "email": "seu_email@exemplo.com"
  }
  ```

### Confirmar Redefinição de Senha
- **Método:** `POST`
- **Endpoint:** `/api/auth/password-reset/confirm/`
- **Descrição:** Define uma nova senha para o usuário usando o código de verificação.
- **Body (raw/json):**
  ```json
  {
      "email": "seu_email@exemplo.com",
      "code": "54321",
      "password": "sua_nova_senha_forte"
  }
  ```

---

## 2. Localidades (`/api/localidades/`)

Rotas para consultar informações de estados, cidades e analisar coordenadas geográficas.

### Listar Estados
- **Método:** `GET`
- **Endpoint:** `/api/localidades/estados/`
- **Descrição:** Retorna uma lista de todos os estados do Brasil.
- **Body:** Nenhum.

### Detalhar Estado
- **Método:** `GET`
- **Endpoint:** `/api/localidades/estados/{id}/`
- **Descrição:** Retorna os detalhes de um estado específico.
- **Body:** Nenhum.

### Listar Cidades
- **Método:** `GET`
- **Endpoint:** `/api/localidades/cidades/`
- **Descrição:** Retorna uma lista de cidades. Pode ser filtrada por estado (ex: `/api/localidades/cidades/?estado=52` para Goiás).
- **Body:** Nenhum.

### Detalhar Cidade
- **Método:** `GET`
- **Endpoint:** `/api/localidades/cidades/{id}/`
- **Descrição:** Retorna os detalhes de uma cidade específica.
- **Body:** Nenhum.

### Analisar Localização por Coordenadas
- **Método:** `GET`
- **Endpoint:** `/api/localidades/analisar/`
- **Descrição:** Recebe coordenadas e retorna a cidade, estado e uma jurisdição sugerida.
- **Query Params:** `latitude` e `longitude` (ex: `/api/localidades/analisar/?latitude=-16.6869&longitude=-49.2648`)
- **Body:** Nenhum.

---

## 3. Denúncias (`/api/denuncias/`)

Rotas para o gerenciamento completo de denúncias, categorias, apoios e comentários.

### Listar Categorias de Denúncia
- **Método:** `GET`
- **Endpoint:** `/api/denuncias/categorias/`
- **Descrição:** Retorna a lista de todas as categorias de denúncia disponíveis.
- **Body:** Nenhum.

### Criar Denúncia (ou Apoiar Existente)
- **Método:** `POST`
- **Endpoint:** `/api/denuncias/denuncias/`
- **Descrição:** Cria uma nova denúncia ou, se uma denúncia similar já existir na proximidade, adiciona um apoio a ela.
- **Body (multipart/form-data):**
  - `titulo`: "Buraco na via"
  - `descricao`: "Há um buraco perigoso na Rua das Flores, em frente ao número 123."
  - `categoria`: 1 (ID da categoria)
  - `cidade`: 5208707 (ID da cidade, ex: Goiânia)
  - `estado`: 52 (ID do estado, ex: Goiás)
  - `latitude`: -16.68690
  - `longitude`: -49.26480
  - `jurisdicao`: "MUNICIPAL"
  - `foto`: (Arquivo de imagem)

### Listar Denúncias
- **Método:** `GET`
- **Endpoint:** `/api/denuncias/denuncias/`
- **Descrição:** Retorna uma lista paginada de denúncias.
- **Body:** Nenhum.

### Detalhar Denúncia
- **Método:** `GET`
- **Endpoint:** `/api/denuncias/denuncias/{id}/`
- **Descrição:** Retorna os detalhes de uma denúncia específica.
- **Body:** Nenhum.

### Atualizar Denúncia
- **Método:** `PUT` / `PATCH`
- **Endpoint:** `/api/denuncias/denuncias/{id}/`
- **Descrição:** Atualiza os dados de uma denúncia. Apenas o autor pode editar.
- **Body (raw/json):** (Campos a serem atualizados)
  ```json
  {
      "titulo": "Título atualizado",
      "descricao": "Descrição atualizada."
  }
  ```

### Deletar Denúncia
- **Método:** `DELETE`
- **Endpoint:** `/api/denuncias/denuncias/{id}/`
- **Descrição:** Remove uma denúncia. Apenas o autor pode deletar.
- **Body:** Nenhum.

### Marcar Denúncia como Resolvida
- **Método:** `POST`
- **Endpoint:** `/api/denuncias/denuncias/{id}/resolver/`
- **Descrição:** Permite que o autor da denúncia a marque com o status "RESOLVIDA".
- **Body:** Nenhum.

### Alterar Status da Denúncia (Ação do Gestor)
- **Método:** `POST`
- **Endpoint:** `/api/denuncias/denuncias/{id}/change_status/`
- **Descrição:** Permite que um Gestor Público com jurisdição altere o status da denúncia.
- **Body (raw/json):**
  ```json
  {
      "status": "EM_ANALISE"
  }
  ```

### Apoiar uma Denúncia
- **Método:** `POST`
- **Endpoint:** `/api/denuncias/apoios/`
- **Descrição:** Cria um novo apoio para uma denúncia existente.
- **Body (raw/json):**
  ```json
  {
      "denuncia": 1 (ID da denúncia a ser apoiada)
  }
  ```

---

## 4. Gestão Pública (`/api/gestao/`)

Rotas exclusivas para usuários do tipo "Gestor Público".

### Listar Minhas Denúncias (Jurisdição)
- **Método:** `GET`
- **Endpoint:** `/api/gestao/minhas-denuncias/`
- **Descrição:** Retorna as denúncias que são de responsabilidade da entidade governamental do gestor logado.
- **Body:** Nenhum.

### Criar Resposta Oficial
- **Método:** `POST`
- **Endpoint:** `/api/gestao/respostas/`
- **Descrição:** Permite que um gestor publique uma resposta oficial para uma denúncia em sua jurisdição.
- **Body (raw/json):**
  ```json
  {
      "denuncia": 1,
      "texto": "Agradecemos o contato. Uma equipe será enviada ao local em até 48 horas para avaliar a situação."
  }
  ```

### Listar Minhas Respostas Oficiais
- **Método:** `GET`
- **Endpoint:** `/api/gestao/respostas/`
- **Descrição:** Lista as respostas oficiais publicadas pela entidade do gestor.
- **Body:** Nenhum.

### Obter Dados do Dashboard
- **Método:** `GET`
- **Endpoint:** `/api/gestao/dashboard/`
- **Descrição:** Retorna dados estatísticos consolidados para o dashboard do gestor.
- **Body:** Nenhum.

### Obter Dados de Denúncias por Período
- **Método:** `GET`
- **Endpoint:** `/api/gestao/dashboard/denuncias-por-periodo/`
- **Descrição:** Retorna a contagem de denúncias agrupadas por período para gráficos.
- **Query Params:** `periodo` (dia, semana, mes, trimestre, ano), `start_date`, `end_date`.
- **Body:** Nenhum.

### Obter Dados para Mapa de Calor (Heatmap)
- **Método:** `GET`
- **Endpoint:** `/api/gestao/dashboard/heatmap/`
- **Descrição:** Retorna as coordenadas e o "peso" (denúncia + apoios) para a geração de um mapa de calor.
- **Body:** Nenhum.