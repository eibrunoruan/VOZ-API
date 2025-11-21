# 🚨 URGENTE: Como Forçar Redesploy no Hostinger

## ⚠️ PROBLEMA: Container não atualiza após `git push`

**Você está deletando e recriando o container pelo link?**  
❌ **Isso puxa código ANTIGO do GitHub (branch default desatualizada)!**

### Prova:
```bash
curl http://72.61.55.172:8000/api/health/
# Retorna: {"status": "ok", "message": "API is running"}
# Deveria retornar: "cloudinary": {"configured": true, "cloud_name": "dphpzghkh"}
```

---

## ✅ SOLUÇÃO CORRETA: Atualizar Container Existente

### **NUNCA delete e recrie o container!**

---

## Método 1: Via Painel Hostinger (RECOMENDADO)

1. **Painel Hostinger** → **Docker** → **voz-do-povo-api**
2. Clique em **"Parar"** (Stop)
3. ⚠️ **NÃO clique em Delete!**
4. Procure por um destes botões:
   - **"Pull Latest"** ou
   - **"Update from Git"** ou
   - **"Rebuild"** ou
   - **"Redesploy from Repository"**
5. Clique na opção encontrada (força `git pull`)
6. Aguarde rebuild terminar
7. Clique em **"Iniciar"** (Start)

---

## Método 2: Via SSH (MAIS CONFIÁVEL)

Se você tem acesso SSH:

```bash
# Conectar
ssh usuario@72.61.55.172
cd /caminho/do/projeto

# Forçar pull dentro do container
docker exec -it voz-do-povo-api bash -c "cd /app && git pull origin main"

# Rebuild completo
docker-compose down
docker-compose up -d --build

# Ver logs
docker logs voz-do-povo-api --tail 50
```

**Deve aparecer:**
```
Cloudinary configuration: cloud_name='dphpzghkh'
```

---

## Método 3: Rebuild Completo (ÚLTIMA OPÇÃO)

Se nada funcionar, rebuild do zero:

```bash
ssh usuario@72.61.55.172
cd /caminho/do/projeto

# Remover TUDO
docker-compose down -v
docker rmi voz-api_web

# Rebuild sem cache
docker-compose build --no-cache
docker-compose up -d

# Verificar commit atual no container
docker exec -it voz-do-povo-api bash -c "cd /app && git log -1 --oneline"
```

---

## 🧪 COMO TESTAR se atualizou:

### 1. Health Check:
```powershell
curl "http://72.61.55.172:8000/api/health/" 2>$null | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

**✅ Resposta CORRETA:**
```json
{
  "status": "ok",
  "cloudinary": {
    "configured": true,
    "cloud_name": "dphpzghkh"
  }
}
```

**❌ Resposta ERRADA (código antigo):**
```json
{
  "status": "ok",
  "message": "API is running"
}
```

### 2. Criar denúncia pelo Flutter:

**✅ URL CORRETA:**
```json
"foto": "https://res.cloudinary.com/dphpzghkh/..."
```

**❌ URL ERRADA:**
```json
"foto": "http://72.61.55.172:8000/media/..."
```

---

## 🔄 AUTOMATIZAR (GitHub Actions)

Arquivo `.github/workflows/deploy.yml` já criado!

### Configurar Webhook:

1. **Hostinger** → **Docker** → **voz-do-povo-api** → **Webhooks**
2. Copie a URL do webhook
3. **GitHub** → **VOZ-API** → **Settings** → **Secrets**
4. Adicione secret: `HOSTINGER_WEBHOOK_URL` = (cola URL)

Agora a cada `git push`, o GitHub aciona redesploy automático! 🎉

---

## 📝 CHECKLIST de Deploy:

- [ ] `git push` feito
- [ ] Container **parado** no Hostinger
- [ ] Container **reconstruído** (não apenas reiniciado!)
- [ ] Container **iniciado**
- [ ] Health check retorna `cloud_name: "dphpzghkh"` ✅
- [ ] Criar denúncia retorna URL Cloudinary ✅

---

**🎯 RESUMO:** Nunca delete e recrie! Sempre use **"Rebuild" ou "Pull Latest"**.
