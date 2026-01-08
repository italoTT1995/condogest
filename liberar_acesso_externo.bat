@echo off
echo ==========================================
echo   LIBERANDO ACESSO EXTERNO (CondoManager)
echo ==========================================
echo.
echo Tentando abrir a porta 5000 no Windows Firewall...
echo.

netsh advfirewall firewall add rule name="CondoManager Server" dir=in action=allow protocol=TCP localport=5000

echo.
echo ==========================================
echo RESULTADO:
echo.
echo Se apareceu "OK" acima:
echo   -> Sucesso! Tente acessar pelo celular agora.
echo.
echo Se apareceu "A operacao solicitada requer elevacao" (Erro):
echo   -> FECHE esta janela.
echo   -> CLIQUE COM O BOTAO DIREITO neste arquivo.
echo   -> Escolha "EXECUTAR COMO ADMINISTRADOR".
echo ==========================================
echo.
pause
