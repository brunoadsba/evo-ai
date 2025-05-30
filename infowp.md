Vou organizar as informações de forma estruturada para configurar seu agente de IA com WhatsApp usando N8N e Evolution API.

# Configuração do Agente IA com WhatsApp via N8N

## Pré-Requisitos

**1º Passo** – Prepare o ambiente:
```bash
mkdir whatsapp-bot
cd whatsapp-bot
```

**2º Passo** – Crie o arquivo docker-compose.yml:
```yaml
version: '3'

services:
  evolution-api:
    image: evolutionapi/evolution:v1.6.0
    restart: always
    ports:
      - "8080:8080"
    environment:
      - AUTHENTICATION_API_KEY=sua_chave_secreta_evolution
    volumes:
      - ./evolution-instances:/evolution/instances
    networks:
      - evolution-network

  n8n:
    image: n8nio/n8n
    restart: always
    ports:
      - "5678:5678"
    environment:
      - N8N_ENCRYPTION_KEY=sua_chave_secreta_n8n
      - N8N_HOST=localhost
      - N8N_PORT=5678
    volumes:
      - ./n8n_data:/home/node/.n8n
    networks:
      - evolution-network

networks:
  evolution-network:
    driver: bridge
```

**3º Passo** – Inicie os containers:
```bash
docker-compose up -d
```

## Configuração da Evolution API

**4º Passo** – Configure a instância do WhatsApp:

- Acesse `http://seuip:8080`
- Clique em "Create Instance"
- Preencha:
  * Nome da instância: `meubot` (ou o nome que preferir)
  * Webhook Url: `http://n8n:5678/webhook/evolution` (será configurado no N8N)
  * Events: Selecione `messages` e `status-messages`
  * Clique em "Create"

**5º Passo** – Conecte o WhatsApp:

- Clique na instância criada
- Na tela de QR Code, escaneie usando o WhatsApp do seu celular
- Aguarde a conexão ser estabelecida

## Configuração do N8N

**6º Passo** – Acesse o N8N:

- Abra no navegador `http://seuip:5678`
- Faça o cadastro inicial

**7º Passo** – Crie um novo Workflow:

- Clique em "Create Workflow"
- Dê um nome como "Agente IA WhatsApp"

**8º Passo** – Adicione o webhook para receber mensagens:

- Na barra de busca de nós, digite "Webhook" e selecione
- Configure:
  * Authentication: None
  * HTTP Method: POST
  * Path: `/webhook/evolution`
  * Response Mode: Last Node
- Salve e ative o webhook clicando no botão de toggle

**9º Passo** – Adicione um nó de filtro para mensagens:

- Adicione um nó "IF"
- Configure a condição:
  * Value 1: `{{$json["body"]["type"]}}`
  * Operation: Equal
  * Value 2: `message`

**10º Passo** – Extraia os dados da mensagem:

- Na opção "true" do IF, adicione um nó "Set"
- Configure as variáveis:
  * Name: messageData
  * Value: JSON
```json
{
  "phone": "{{$json.body.key.remoteJid.split('@')[0]}}",
  "message": "{{$json.body.message.conversation || $json.body.message.extendedTextMessage?.text}}",
  "name": "{{$json.body.pushName}}",
  "instanceName": "{{$json.body.key.id.split(':')[0]}}",
  "messageId": "{{$json.body.key.id}}"
}
```

**11º Passo** – Integre com seu agente de IA:

- Adicione um nó HTTP Request (ou o nó específico para sua plataforma de IA)
- Para OpenAI, configure:
  * Method: POST
  * URL: `https://api.openai.com/v1/chat/completions`
  * Authentication: Header Auth
  * Auth: `Bearer sua_chave_api_openai`
  * Headers: Content-Type: application/json
  * Request Body: JSON
```json
{
  "model": "gpt-4o",
  "messages": [
    {
      "role": "system",
      "content": "Você é um assistente virtual atendendo pelo WhatsApp. Seja conciso e direto nas respostas."
    },
    {
      "role": "user",
      "content": "{{$node['Set'].json.messageData.message}}"
    }
  ],
  "temperature": 0.7
}
```

**12º Passo** – Extraia a resposta do agente:

- Adicione um novo nó "Set"
- Configure:
  * Name: agentResponse
  * Value: String
  * `{{$json.choices[0].message.content}}`

**13º Passo** – Envie a resposta de volta ao WhatsApp:

- Adicione outro nó "HTTP Request"
- Configure:
  * Method: POST
  * URL: `http://evolution-api:8080/message/sendText/meubot`
  * Authentication: Header Auth
  * Auth: `Bearer sua_chave_secreta_evolution` (a mesma do docker-compose)
  * Headers: Content-Type: application/json
  * Request Body: JSON
```json
{
  "number": "{{$node['Set'].json.messageData.phone}}",
  "options": {
    "delay": 1000
  },
  "textMessage": {
    "text": "{{$node['agentResponse'].json}}"
  }
}
```

**14º Passo** – Ative o workflow:

- Clique no botão "Save" no canto superior direito
- Ative o workflow com o toggle "Active"

## Testando a Integração

**15º Passo** – Envie uma mensagem para o número conectado:

- Use outro celular para enviar uma mensagem para o número conectado à Evolution API
- Observe se a mensagem chega no N8N (verifique o log de execução)
- Verifique se a resposta do agente é enviada de volta ao WhatsApp

## Configurações Adicionais

### Para mensagens multimídia (imagens, áudio):

**16º Passo** – Adicione tratamento de mídia:

- Expanda o nó IF para incluir condições para outros tipos de mensagens:
```
$json.body.message.hasOwnProperty('imageMessage') || 
$json.body.message.hasOwnProperty('audioMessage') || 
$json.body.message.hasOwnProperty('documentMessage')
```

### Para integrar webhooks de status:

**17º Passo** – Adicione um branch separado para status:

- No nó IF original, adicione uma condição para `$json.body.type == 'status'`
- Crie um fluxo específico para lidar com as atualizações de status

## Otimizações

**18º Passo** – Configure o tratamento de erros:

- Adicione nós "Error Trigger" para lidar com falhas
- Configure respostas padrão caso a API de IA não responda

**19º Passo** – Implemente controle de conversas:

- Use o armazenamento interno do N8N ou um banco de dados externo para manter o contexto das conversas
- Adicione nós para persistir e recuperar históricos de conversa

**20º Passo** – Configure Auto-saving do workflow:

- Em Settings > Workflows, habilite auto-saving para evitar perda de trabalho

Esta configuração fornece uma base sólida para conectar seu agente de IA ao WhatsApp. Você pode expandir e personalizar de acordo com suas necessidades específicas.