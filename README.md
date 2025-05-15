#  Chatbot via WhatsApp

Este projeto implementa um chatbot automatizado usando **n8n**, **API Oficial do WhatsApp (Meta)**, **OpenAI GPT-3.5** e **Supabase** para confirmação de consultas, exames e vacinas da rede pública de saúde.

---

## 📌 Funcionalidades

- ✅ Envio automático de mensagens de confirmação para pacientes via WhatsApp
- 📥 Recebimento das respostas e tratamento via n8n
- 🤖 Respostas automáticas via API do ChatGPT (quando necessário)
- 💾 Salvamento de logs e mensagens no banco de dados PostgreSQL/Supabase
- 📊 Organização do fluxo via painel visual no n8n
- 🧾 Envio de filipeta de agendamento simulada ao final da conversa

---

## 🛠️ Tecnologias Utilizadas

### 2.1 Backend e Automação

- `n8n`: Plataforma de automação no-code usada para orquestrar o fluxo de mensagens
- `Python + FastAPI`: API auxiliar para salvar mensagens no banco
- `Supabase`: Banco de dados PostgreSQL hospedado na nuvem
- `Vercel`: Hospedagem gratuita para API FastAPI

### 2.2 Integração com WhatsApp

- `Meta WhatsApp Cloud API`: Canal oficial para envio e recebimento de mensagens
- `Webhook n8n`: Captura das mensagens recebidas
- `Template Message`: Usado para envio de mensagens fora da janela de 24h

### 2.3 Processamento de Mensagens com IA

- `OpenAI GPT-3.5 Turbo`: Utilizado para responder perguntas abertas ou genéricas
- `Switch Node`: Gera decisões para respostas predefinidas

### 2.4 Banco de Dados

- `Supabase (PostgreSQL)`: Armazena usuários, mensagens, respostas e logs
- `Tabelas`: users, messages, logs, bot_config, predefined_responses

---

## 🔄 Fluxo de Automação

```mermaid
graph TD;
    A[Webhook Recebe Mensagem] --> B{Mensagem pré-definida?};
    B -- Sim --> C[Retorna resposta pronta];
    B -- Não --> D[Consulta na OpenAI];
    C --> E[Salva no Supabase];
    D --> F[Formata resposta];
    F --> G[Envia mensagem WhatsApp];
    G --> E;
