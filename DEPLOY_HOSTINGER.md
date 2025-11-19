# Deploy no Hostinger via Docker Compose

## Passo 1: Acessar o Gerenciador Docker

1. Entre no painel da Hostinger
2. Vá em **Gerenciador Docker**
3. Clique em **"Implante seu primeiro site ou aplicativo com Docker Compose"**

## Passo 2: Deploy via URL do GitHub

1. Escolha a opção: **"Compose a partir de URL"**
2. Cole a URL do seu repositório GitHub:
   ```
   https://github.com/eibrunoruan/VOZ-API
   ```
3. O Hostinger vai detectar automaticamente o `docker-compose.yml`

## Passo 3: Configurar Variáveis de Ambiente

No painel do Hostinger, configure as seguintes variáveis de ambiente:

```env
SECRET_KEY=sua_secret_key_aqui_use_um_gerador
DEBUG=False
ALLOWED_HOSTS=seu-dominio.com,www.seu-dominio.com

DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
DB_USER=postgres.wppptrpoxhtgqvahxfto
DB_PASSWORD=84731079Bruno#13102004
DB_HOST=aws-1-sa-east-1.pooler.supabase.com
DB_PORT=6543

BREVO_SMTP_USER=seu_email@exemplo.com
BREVO_SMTP_PASSWORD=sua_senha_brevo
EMAIL_HOST=smtp-relay.brevo.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=Voz do Povo <noreply@vozodopovo.com>

CORS_ALLOW_ALL_ORIGINS=False
CORS_ALLOWED_ORIGINS=https://seu-dominio.com
CSRF_TRUSTED_ORIGINS=https://seu-dominio.com
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True

NOMINATIM_API_ENDPOINT=https://nominatim.openstreetmap.org/reverse
NOMINATIM_USER_AGENT=VozDoPovo Backend
```

## Passo 4: Iniciar o Container

1. Clique em **"Deploy"** ou **"Iniciar"**
2. Aguarde o build da imagem (pode levar alguns minutos)
3. O container será iniciado automaticamente na porta 8000

## Passo 5: Rodar Migrações (Primeira vez)

Após o container subir, acesse o terminal do container no painel Hostinger e execute:

```bash
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py populate_cities
python manage.py createsuperuser
```

## Passo 6: Configurar Domínio

1. No painel Hostinger, vá em **Domínios**
2. Configure o proxy reverso para apontar para `localhost:8000`
3. Habilite SSL/HTTPS

## Verificação

Acesse: `https://seu-dominio.com/api/health/`

Se retornar `{"status": "ok"}`, está funcionando! ✅

## Comandos Úteis

**Ver logs do container:**
```bash
docker-compose logs -f web
```

**Reiniciar container:**
```bash
docker-compose restart web
```

**Parar container:**
```bash
docker-compose down
```

**Atualizar código (após git push):**
```bash
docker-compose down
docker-compose pull
docker-compose up -d
```

## Troubleshooting

**Erro de conexão com banco:**
- Verifique as credenciais do Supabase
- Confirme que DB_HOST e DB_PORT estão corretos

**Erro 502 Bad Gateway:**
- Container pode não ter iniciado
- Verifique os logs: `docker-compose logs web`

**Static files não carregam:**
- Execute: `python manage.py collectstatic --noinput`
- Reinicie o container
