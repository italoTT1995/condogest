@echo off
title Condo Manager - Servidor
color 0A

echo ---------------------------------------------------
echo    INICIANDO O SISTEMA DE GESTAO DE CONDOMINIO
echo ---------------------------------------------------
echo.

:: Ativar ambiente virtual (ajuste o caminho se necessario)
call venv\Scripts\activate.bat

:: Iniciar servidor
python run_prod.py

pause
