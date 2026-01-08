@echo off
chcp 65001 >nul
echo ==========================================
echo   ENVIANDO CÓDIGO PARA O GITHUB 🚀
echo ==========================================
echo.
echo 1. Verificando conexão com: https://github.com/GoodLuckMyWay/condogest.git
git remote set-url origin https://github.com/GoodLuckMyWay/condogest.git

echo.
echo 2. Preparando arquivos...
git add .
git commit -m "Atualizacao automatica via Script" 
REM O commit pode falhar se não houver nada novo, tudo bem.

echo.
echo 3. Enviando para a nuvem...
echo    ATENCAO: Se abrir uma janela de login, faca o login!
echo.
git branch -M main
git push -u origin main

echo.
echo ==========================================
if %errorlevel% equ 0 (
    echo   SUCESSO! SEU CODIGO ESTA NO GITHUB ✅
) else (
    echo   OPS! ALGO DEU ERRADO. VEJA A MENSAGEM ACIMA ❌
)
echo ==========================================
pause
