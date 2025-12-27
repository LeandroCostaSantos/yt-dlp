@echo off
chcp 65001 >nul
title YT-DLP GUI - Iniciando...

echo ╔══════════════════════════════════════════════════════════════╗
echo ║                     YT-DLP GUI                               ║
echo ║              Baixador de Videos do YouTube                   ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

:: Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao foi encontrado!
    echo.
    echo Por favor, instale o Python em: https://www.python.org/downloads/
    echo Marque a opcao "Add Python to PATH" durante a instalacao!
    echo.
    pause
    exit /b 1
)

echo [OK] Python encontrado!
echo.

:: Verificar e instalar Pillow se necessário
echo Verificando dependencias...
python -c "from PIL import Image" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Instalando Pillow (para exibir thumbnails)...
    pip install Pillow --quiet
    if errorlevel 1 (
        echo [AVISO] Nao foi possivel instalar Pillow. Thumbnails nao serao exibidas.
    ) else (
        echo [OK] Pillow instalado com sucesso!
    )
) else (
    echo [OK] Pillow ja instalado!
)

echo.
echo Iniciando YT-DLP GUI...
echo.

:: Executar a GUI
cd /d "%~dp0"
python run_gui.py

if errorlevel 1 (
    echo.
    echo [ERRO] Ocorreu um erro ao executar o programa.
    pause
)
