@echo off
echo ===================================================
echo   INICIANDO SISTEMA FINANCEIRO JURIDICO
echo ===================================================
echo.
echo Certifique-se de que o Docker Desktop esta rodando.
echo.

cd /d "%~dp0"

echo Parando containers antigos (se houver)...
docker-compose down

echo.
echo Construindo e iniciando os servicos...
docker-compose up -d --build

echo.
echo ===================================================
echo   SISTEMA INICIADO!
echo ===================================================
echo.
echo Acesse no navegador: http://financas
echo.
pause
