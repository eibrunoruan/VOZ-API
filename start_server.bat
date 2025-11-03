@echo off
echo ================================================
echo     VOZ DO POVO - Backend Django Server
echo ================================================
echo.

echo [1/4] Verificando IP do PC...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr "IPv4"') do (
    set IP=%%a
    goto :found_ip
)
:found_ip
echo        IP encontrado:%IP%
echo.

echo [2/4] Verificando dependencias...
pip show django >nul 2>&1
if errorlevel 1 (
    echo        ❌ Django nao instalado!
    echo        Instalando dependencias...
    pip install -r requirements.txt
) else (
    echo        ✅ Django instalado
)
echo.

echo [3/4] Aplicando migracoes do banco de dados...
python manage.py migrate
echo.

echo [4/4] Iniciando servidor Django...
echo.
echo ================================================
echo     BACKEND RODANDO EM:
echo     - Local:   http://localhost:8000
echo     - Rede:    http:%IP%:8000
echo.
echo     Endpoints importantes:
echo     - Admin:      http:%IP%:8000/admin/
echo     - API:        http:%IP%:8000/api/
echo     - Denuncias:  http:%IP%:8000/api/denuncias/denuncias/
echo.
echo     Pressione CTRL+C para parar o servidor
echo ================================================
echo.

python manage.py runserver 0.0.0.0:8000
