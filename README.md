# 🤖 Chatbot de Atendimento (Vendas / Instrutor) via WhatsApp

Este projeto é um fluxo de atendimento inteligente via WhatsApp, automatizado com **n8n**, **OpenAI GPT-3.5 Turbo**, **WhatsApp Cloud API (Meta)** e **Supabase**. Ele é voltado para responder dúvidas de usuários sobre serviços de vendas, produtos ou agendamento com instrutor, oferecendo respostas inteligentes e armazenando os registros no banco de dados.

---

## 📌 Funcionalidades

- ✅ Recebimento de mensagens via Webhook do WhatsApp
- 🔁 Verificação de palavras-chave para resposta rápida (pré-definidas)
- 💬 Geração de resposta via ChatGPT se não houver correspondência
- 📲 Envio automatizado da resposta no próprio WhatsApp
- 💾 Armazenamento das interações no Supabase (mensagens e respostas)

---

## 🛠️ Tecnologias Utilizadas

### Backend e Orquestração

- **n8n**: Fluxo visual de automação
- **Python + FastAPI**: API auxiliar (opcional) para gravação de dados
- **Supabase**: Banco de dados PostgreSQL gerenciado
- **Vercel**: Hospedagem gratuita da API de backend

### Integração e Mensageria

- **Meta WhatsApp Cloud API**: Canal oficial para envio e recebimento
- **Webhook n8n**: Captura das mensagens recebidas
- **ChatGPT API (OpenAI)**: Para gerar respostas inteligentes

---

## 🔄 Fluxo Automatizado

```mermaid
graph TD;
  A[Webhook Recebe Mensagem] --> B{Mensagem pré-definida?}
  B -- Sim --> C[Resposta pronta via Opção de Resposta]
  C --> D[Montar Resposta Final]
  D --> E[Enviar via WhatsApp]
  E --> F[Salvar no Supabase]

  B -- Não --> G[Chamar ChatGPT 3.5 Turbo]
  G --> H[Montar Resposta IA]
  H --> I[Enviar via WhatsApp]
  I --> F


