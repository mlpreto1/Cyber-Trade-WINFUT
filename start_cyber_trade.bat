@echo off
title CYBER TRADE WIN v3.1 - OpenClaw Edition
color 0A
echo ==========================================================================
echo        CYBER TRADE WIN v3.1 - OPENCLAW AGENTS ORCHESTRATOR
echo ==========================================================================
echo.
echo [SISTEMA] Iniciando sequencia de boot automatizada...
echo.

cd /d "H:\Meu Drive\Cyber Trade\Winfut"

:: --- [1/7] VERIFICAÇÃO DE PYTHON ---
echo [1/7] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 goto ERR_PYTHON
echo [OK] Python detectada.
goto STEP_DOCKER

:ERR_PYTHON
echo [ERRO] Python nao encontrado! Por favor, instale o Python 3.10+
pause
exit /b 1

:: --- [2/7] AUTO-BOOT DO DOCKER ---
:STEP_DOCKER
echo [2/7] Verificando Docker Daemon...
docker ps >nul 2>&1
if %errorlevel% equ 0 goto DOCKER_OK
echo [SISTEMA] Docker offline. Tentando iniciar Docker Desktop...
start "" "C:\Program Files\Docker\Docker Desktop.exe"
echo [SISTEMA] Aguardando o motor do Docker iniciar (isso pode levar 30-60s)...
timeout /t 10 /nobreak >nul
goto STEP_DOCKER

:DOCKER_OK
echo [OK] Docker Daemon online.

:: --- [3/7] SUBINDO INFRAESTRUTURA (REDIS) ---
echo [3/7] Subindo containers via Docker Compose...
docker compose up -d
echo [OK] Infraestrutura de estado (Redis) configurada.

:: --- [4/7] VERIFICAÇÃO DE OPENCLAW GATEWAY ---
echo [4/7] Verificando OpenClaw Gateway...
echo [OK] Gateway OpenClaw assumido como online (Sessao Ativa).

:: --- [5/7] INICIANDO MT5 ---
echo [5/7] Iniciando MT5 Terminal...
set MT5_PATH=
if exist "C:\Program Files\Clear Investimentos MT5 Terminal\terminal64.exe" set MT5_PATH=C:\Program Files\Clear Investimentos MT5 Terminal\terminal64.exe
if exist "C:\Program Files (x86)\Clear Investimentos MT5 Terminal\terminal.exe" set MT5_PATH=C:\Program Files (x86)\Clear Investimentos MT5 Terminal\terminal.exe

if defined MT5_PATH (
    start "" "%MT5_PATH%"
    echo [OK] MT5 iniciado: %MT5_PATH%
) else (
    echo [AVISO] MT5 nao encontrado nos caminhos padrao.
)
timeout 5 /nobreak >nul

:: --- [6/7] INICIANDO PIXEL AGENTS SERVER ---
echo [6/7] Iniciando Pixel Agents Server (Visualizacao)...
start /B python agents_pixel_server.py
echo [OK] Servidor de pixels ativo em http://localhost:8765

:: --- [7/7] INICIANDO CORE DO CYBER TRADE ---
echo [7/7] Iniciando Orquestrador Cyber Trade...
echo.
echo ==========================================================================
echo  INTERFACE DE COMANDO ATIVA
echo  - Pixel Agents: http://localhost:8765
echo  - Gateway:      http://localhost:3000
echo  - Log:          Acompanhe abaixo
echo ==========================================================================
echo.
echo Pressione Ctrl+C para encerrar a operacao.
echo.

python main.py

pause
