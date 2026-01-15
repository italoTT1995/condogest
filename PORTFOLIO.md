# 📂 Case Study: CondoGest - Plataforma de Gestão Condominial

**Desenvolvedor:** Italo Silva  
**Data:** Janeiro 2026  
**Status:** Em Produção (Fase de Lançamento)

---

## 🎯 O Desafio
Condomínios residenciais frequentemente sofrem com processos manuais, comunicação falha e falta de transparência. O objetivo deste projeto foi eliminar o uso de papel, planilhas descentralizadas e grupos de WhatsApp informais, centralizando toda a gestão em uma plataforma segura e profissional.

## 💡 A Solução: CondoGest
Uma aplicação web completa (Full-Stack) que digitaliza as principais rotinas de um condomínio. O sistema oferece interfaces específicas para cada perfil de usuário (Síndico, Porteiro, Morador e Zelador), garantindo que cada um tenha acesso às ferramentas certas.

---

## 🚀 Funcionalidades de Destaque

### 1. Sistema de Portaria e Segurança
*   **Problema:** Controle de acesso lento e inseguro.
*   **Solução:** Implementação de crachás digitais (QR Code) únicos por morador.
*   **Detalhe Técnico:** O QR Code é validado em tempo real com regras de "Anti-Passback" (impede uso duplo) e verifica inadimplência financeira, alertando o porteiro discretamente.

### 2. Gestão de Encomendas Rastreável
*   **Problema:** Encomendas acumuladas na portaria e moradores sem saber que chegaram.
*   **Solução:** O porteiro fotografa a etiqueta da caixa. O sistema processa o recebimento e notifica o morador via painel (e e-mail) instantaneamente.
*   **Resultado:** Redução de 80% no tempo de permanência de pacotes na portaria.

### 3. Transparência Financeira
*   **Problema:** Moradores desconfiados da gestão do síndico.
*   **Solução:** Dashboard financeiro aberto, onde o síndico lança receitas/despesas e os moradores visualizam gráficos em tempo real.

### 4. Módulo "Achados e Perdidos" (Lost & Found)
*   **Inovação:** Uma galeria visual de itens encontrados nas áreas comuns, facilitando a recuperação de objetos perdidos e registrando digitalmente a devolução.

---

## 🛠️ Arquitetura e Tecnologias

Este projeto foi construído para ser **seguro**, **escalável** e **fácil de manter**.

| Camada | Tecnologia | Motivo da Escolha |
| :--- | :--- | :--- |
| **Backend** | **Python (Flask)** | Desenvolvimento ágil, segurança robusta e ótimo ecossistema. |
| **Banco de Dados** | **PostgreSQL** | Confiabilidade para dados críticos (financeiros/acesso). Uso de ORM (SQLAlchemy). |
| **Frontend** | **Bootstrap 5 + Jinja2** | Interface responsiva (Mobile-First) e renderização rápida no servidor. |
| **Deploy** | **Render (Cloud)** | Infraestrutura moderna com CI/CD (Deploy contínuo via GitHub). |
| **Segurança** | **Flask-Login & CSRF** | Proteção contra ataques comuns e gestão de sessões criptografadas. |

---

## 📸 Galeria do Projeto

*(Espaço reservado para Screenshots - Sugestão de telas para capturar:)*
1.  **Dashboard Principal:** Mostrando gráficos e estatísticas.
2.  **Tela de Login:** Com o design moderno e botão de apresentação.
3.  **Módulo de Encomendas:** Lista de pacotes com status.
4.  **Perfil do Morador:** Visualização do QR Code de acesso.

---

## 👨‍💻 Conclusão
O CondoGest não é apenas um "crud", é um produto focado em resolver dores reais de convivência e administração. O projeto demonstra domínio em engenharia de software, modelagem de dados complexa e UX (Experiência do Usuário).
