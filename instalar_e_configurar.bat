@echo off
echo Instalando dependencias...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Erro na instalacao das dependencias. Verifique se o Python/Pip esta no PATH.
    pause
    exit /b %errorlevel%
)

echo.
echo Criando tabelas no banco de dados...
python setup_db.py
if %errorlevel% neq 0 (
    echo Erro ao criar o banco de dados. Verifique se o PostgreSQL esta rodando e o banco 'condominio' existe.
    pause
    exit /b %errorlevel%
)

echo.
echo Sucesso! Agora execute o arquivo 'iniciar_sistema.bat' para abrir o site.
pause
