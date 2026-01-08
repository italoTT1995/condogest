@echo off
title Condo Manager - Backup do Banco de Dados
color 0E

echo ---------------------------------------------------
echo       GERANDO BACKUP DO BANCO DE DADOS...
echo ---------------------------------------------------

:: Definir variaveis
set PG_DUMP="C:\Program Files\PostgreSQL\18\bin\pg_dump.exe"
set DB_NAME=condominio
set DB_USER=postgres
set DB_HOST=localhost
set BACKUP_DIR=backups

:: Timestamp para nome do arquivo (YYYY-MM-DD_HH-MM)
set TIMESTAMP=%date:~6,4%-%date:~3,2%-%date:~0,2%_%time:~0,2%-%time:~3,2%
set TIMESTAMP=%TIMESTAMP: =0%
set TIMESTAMP=%TIMESTAMP::=-%

:: Senha do banco (Atencao: Em prod real, use .pgpass file)
set PGPASSWORD=root

:: Criar pasta se nao existir
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

:: Nome do arquivo final
set FILENAME=%BACKUP_DIR%\backup_%TIMESTAMP%.sql

echo.
echo Conectando ao banco '%DB_NAME%'...
echo Usuario: %DB_USER%
echo Arquivo: %FILENAME%
echo.

:: Executar backup
:: PGPASSWORD pode ser necessario se nao tiver configurado o pgpass. 
:: Por seguranca, em prod real, use .pgpass file. Aqui vamos pedir senha ou assumir trust para localhost dev.
%PG_DUMP% -h %DB_HOST% -U %DB_USER% -F p -b -v -f "%FILENAME%" %DB_NAME%

if %ERRORLEVEL% equ 0 (
    color 0A
    echo.
    echo ---------------------------------------------------
    echo           BACKUP REALIZADO COM SUCESSO!
    echo ---------------------------------------------------
    echo Arquivo salvo em: %FILENAME%
) else (
    color 0C
    echo.
    echo ---------------------------------------------------
    echo           ERRO AO REALIZAR BACKUP
    echo ---------------------------------------------------
    echo Verifique se o caminho do pg_dump esta correto e se o servidor esta rodando.
)

pause
