@echo off
title CondoGest - GERADOR DE LINK PARA CELULAR / DEMONSTRACAO
color 0B

echo ---------------------------------------------------
echo    GERANDO LINK SEGURO (HTTPS) PARA DEMONSTRACAO
echo ---------------------------------------------------
echo.
echo 1. O sistema deve estar rodando (iniciar_sistema.bat aberto).
echo 2. Aguarde carregar... procure pela linha que diz:
echo.
echo    "Your quick tunnel has been created! Visit it at:"
echo    "https://algum-nome-aleatorio.trycloudflare.com"
echo.
echo 3. ESSE EH O LINK que voce deve abrir no celular ou mandar pro cliente!
echo.
echo ---------------------------------------------------
echo Pressione CTRL+C para parar o link de demonstração.
echo ---------------------------------------------------
echo.

.\cloudflared.exe tunnel --url http://localhost:8080

pause
