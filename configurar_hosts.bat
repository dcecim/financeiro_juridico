@echo off
echo ===================================================
echo   CONFIGURACAO DE HOSTS - SISTEMA FINANCEIRO
echo ===================================================
echo.
echo Este script adicionara a entrada '127.0.0.1 financas' ao seu arquivo hosts.
echo NECESSARIO EXECUTAR COMO ADMINISTRADOR.
echo.

set HOSTS_FILE=%WINDIR%\System32\drivers\etc\hosts
set DOMAIN=financas

findstr /C:"%DOMAIN%" "%HOSTS_FILE%" >nul
if %errorlevel% == 0 (
    echo O dominio '%DOMAIN%' ja esta configurado.
) else (
    echo Adicionando '%DOMAIN%' ao arquivo hosts...
    echo. >> "%HOSTS_FILE%"
    echo 127.0.0.1 %DOMAIN% >> "%HOSTS_FILE%"
    echo Configurado com sucesso!
)

pause
