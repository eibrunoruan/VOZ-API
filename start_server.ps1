# Script de Diagnóstico e Inicialização do Backend Django
# Voz do Povo - Backend

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "    VOZ DO POVO - Backend Django Server" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar IP
Write-Host "[1/6] Verificando IP do PC..." -ForegroundColor Yellow
$ipInfo = Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -like "192.168.*" } | Select-Object -First 1
if ($ipInfo) {
    $ip = $ipInfo.IPAddress
    Write-Host "      ✅ IP encontrado: $ip" -ForegroundColor Green
} else {
    Write-Host "      ⚠️  IP não encontrado na faixa 192.168.x.x" -ForegroundColor Yellow
    $ip = "localhost"
}
Write-Host ""

# 2. Verificar se a porta 8000 está livre
Write-Host "[2/6] Verificando porta 8000..." -ForegroundColor Yellow
$portInUse = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($portInUse) {
    Write-Host "      ⚠️  Porta 8000 já está em uso!" -ForegroundColor Yellow
    Write-Host "      Encerrando processo..." -ForegroundColor Yellow
    $process = Get-Process -Id $portInUse.OwningProcess -ErrorAction SilentlyContinue
    if ($process) {
        Stop-Process -Id $process.Id -Force
        Write-Host "      ✅ Processo encerrado" -ForegroundColor Green
    }
} else {
    Write-Host "      ✅ Porta 8000 disponível" -ForegroundColor Green
}
Write-Host ""

# 3. Verificar Python
Write-Host "[3/6] Verificando instalação do Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "      ✅ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "      ❌ Python não encontrado!" -ForegroundColor Red
    Write-Host "      Instale Python 3.8+ de https://python.org" -ForegroundColor Red
    pause
    exit
}
Write-Host ""

# 4. Verificar dependências
Write-Host "[4/6] Verificando dependências..." -ForegroundColor Yellow
$djangoInstalled = pip show django 2>&1 | Select-String "Name: Django"
if ($djangoInstalled) {
    Write-Host "      ✅ Django instalado" -ForegroundColor Green
} else {
    Write-Host "      ❌ Django não instalado!" -ForegroundColor Red
    Write-Host "      Instalando dependências..." -ForegroundColor Yellow
    pip install -r requirements.txt
}
Write-Host ""

# 5. Aplicar migrações
Write-Host "[5/6] Aplicando migrações do banco de dados..." -ForegroundColor Yellow
python manage.py migrate --noinput
if ($LASTEXITCODE -eq 0) {
    Write-Host "      ✅ Migrações aplicadas com sucesso" -ForegroundColor Green
} else {
    Write-Host "      ⚠️  Erro ao aplicar migrações" -ForegroundColor Yellow
}
Write-Host ""

# 6. Verificar regras de firewall
Write-Host "[6/6] Verificando firewall..." -ForegroundColor Yellow
$firewallRule = Get-NetFirewallRule -DisplayName "Django Dev Server" -ErrorAction SilentlyContinue
if ($firewallRule) {
    Write-Host "      ✅ Regra de firewall configurada" -ForegroundColor Green
} else {
    Write-Host "      ⚠️  Regra de firewall NÃO encontrada" -ForegroundColor Yellow
    Write-Host "      O celular pode ter problemas para conectar." -ForegroundColor Yellow
    Write-Host ""
    $createRule = Read-Host "      Deseja criar a regra de firewall agora? (S/N)"
    if ($createRule -eq "S" -or $createRule -eq "s") {
        try {
            New-NetFirewallRule -DisplayName "Django Dev Server" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow -ErrorAction Stop
            Write-Host "      ✅ Regra de firewall criada! (Requer permissões de Admin)" -ForegroundColor Green
        } catch {
            Write-Host "      ❌ Erro ao criar regra. Execute este script como Administrador." -ForegroundColor Red
        }
    }
}
Write-Host ""

# Resumo
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "     INICIANDO SERVIDOR DJANGO" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  📍 Acesso Local:" -ForegroundColor White
Write-Host "     http://localhost:8000" -ForegroundColor Cyan
Write-Host ""
Write-Host "  📱 Acesso do Celular:" -ForegroundColor White
Write-Host "     http://$ip:8000" -ForegroundColor Cyan
Write-Host ""
Write-Host "  🔗 Endpoints Importantes:" -ForegroundColor White
Write-Host "     • Admin:     http://$ip:8000/admin/" -ForegroundColor Gray
Write-Host "     • API Root:  http://$ip:8000/api/" -ForegroundColor Gray
Write-Host "     • Denúncias: http://$ip:8000/api/denuncias/denuncias/" -ForegroundColor Gray
Write-Host ""
Write-Host "  ⚙️  Configurações:" -ForegroundColor White
Write-Host "     • CORS: Habilitado (todas as origens)" -ForegroundColor Gray
Write-Host "     • ALLOWED_HOSTS: *, $ip, localhost" -ForegroundColor Gray
Write-Host ""
Write-Host "  ⏹️  Para parar: Pressione CTRL+C" -ForegroundColor Yellow
Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Iniciar servidor
python manage.py runserver 0.0.0.0:8000
