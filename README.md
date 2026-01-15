# 🏢 CondoGest - Sistema de Gestão de Condomíios Inteligente

![CondoGest Banner](app/static/img/logo.png)

> **Gestão completa, moderna e eficiente para condomíios residenciais.**  
> O CondoGest centraliza portaria, financeiro, reservas e comunicação em uma única plataforma web/mobile.

## 🚀 Sobre o Projeto

O **CondoGest** é uma solução *Full-Stack* desenvolvida para modernizar a administração de condomínios. Ele elimina o uso de papel e planilhas desconexas, oferecendo um painel administrativo robusto para síndicos e um aplicativo intuitivo para moradores e porteiros.

O sistema foi desenhado com foco em **segurança** (controle de acesso via QR Code), **transparência** (prestação de contas em tempo real) e **agilidade** (notificações de encomendas e avisos).

## 🛠️ Tech Stack (Tecnologias)

O projeto utiliza uma arquitetura moderna e escalável:

*   **Backend:** Python 3.11+, Flask (Microframework robusto)
*   **Banco de Dados:** PostgreSQL (SQLAlchemy ORM)
*   **Frontend:** Bootstrap 5, HTML5, CSS3, JavaScript (Vanilla)
*   **Autenticação:** Flask-Login (Sessions & Cookies seguros)
*   **Hospedagem:** Render.com (Deployment contínuo)

## ✨ Principais Funcionalidades

### 🔐 1. Portaria Inteligente & Controle de Acesso
*   **QR Code Dinâmico:** Moradores usam um crachá digital para acesso.
*   **Registro de Visitantes:** Cadastro rápido com foto e registro de entrada/saída.
*   **Logs de Acesso:** Histórico completo de quem entrou e saiu do condomínio.

### 📦 2. Gestão de Encomendas
*   **Registro Fotográfico:** O porteiro tira foto da encomenda ao receber.
*   **Notificações:** O morador é avisado instantaneamente, reduzindo o tempo de permanência de pacotes na portaria.
*   **Histórico:** Controle de entregas pendentes e retiradas.

### 💰 3. Módulo Financeiro & Transparência
*   **Boletos Digitais:** Geração e visualização de boletos.
*   **Prestação de Contas:** Gráficos e relatórios de receitas vs. despesas em tempo real.
*   **Pagamentos:** Gestão de status de inadimplência (com alertas discretos na portaria).

### 🗓️ 4. Reservas de Áreas Comuns
*   **Agendamento Online:** Moradores reservam Salão de Festas, Churrasqueira, etc.
*   **Regras Automatizadas:** Bloqueio de datas duplicadas e verificação de antecedência (ex: mín 24h).

### 📢 5. Comunicação & Chamados
*   **Mural de Avisos:** Comunicados oficiais do síndico para todos.
*   **Tickets (Chamados):** Moradores abrem reclamações ou solicitações (ex: "Lâmpada queimada"), com acompanhamento de status.

### 🧸 6. Achados e Perdidos (Novo!)
*   **Catálogo Visual:** Cadastro de itens encontrados com foto e local.
*   **Resgate Seguro:** Fluxo de devolução com registro de quem retirou.

## 📱 Instalação e Execução Local

Para rodar o projeto em sua máquina para desenvolvimento:

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/SeuUsuario/condogest.git
    cd condogest
    ```

2.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configuração do Banco de Dados:**
    *   Certifique-se de ter o PostgreSQL instalado.
    *   Configure a URI do banco no arquivo `.env` ou `config.py`.

4.  **Execute o servidor:**
    ```bash
    python run.py
    ```
    O sistema estará acessível em `http://localhost:5000`.

## 📸 Galeria (Screenshots)

*Em breve: Adicione aqui prints das telas principais (Dashboard, Portaria, App Mobile).*

---

Desenvolvido por **Italo Silva**.
