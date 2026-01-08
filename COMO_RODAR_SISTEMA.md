# 🏢 Como Rodar o Sistema de Condomínio

Este guia explica como iniciar o sistema na sua máquina e como acessar pelo celular.

## 1. Início Rápido (Local)
Para rodar o sistema no seu computador:

1. Dê dois cliques no arquivo:
   👉 **`iniciar_sistema.bat`**

2. Uma janela preta vai abrir. Aguarde aparecer a mensagem:
   `Running on http://127.0.0.1:5000`

3. Acesse no navegador:
   🔗 [http://localhost:5000](http://localhost:5000)

---

## 2. Acessar pelo Celular (Wi-Fi)
Para testar a câmera ou acessar de outro dispositivo na mesma rede:

1. Dê dois cliques no arquivo:
   👉 **`liberar_acesso_externo.bat`**

2. Ele vai mostrar o **Endereço IP** do seu computador (ex: `192.168.0.15`).

3. No celular, digite esse endereço seguido de `:5000`. Exemplo:
   `http://192.168.0.15:5000`

---

## 3. Login de Teste
Usuários já cadastrados (exemplo):

- **Morador**: `usuario` / `senha`
- **Porteiro**: `porteiro` / `senha`
- **Admin**: `admin` / `admin`

---

## ⚠️ Problemas Comuns
- **Erro de "CSRF Token"**: Atualize a página (F5) e tente de novo.
- **Não conecta no celular**: Verifique se o computador e o celular estão no mesmo Wi-Fi e se o firewall não está bloqueando.
