const wppconnect = require('@wppconnect-team/wppconnect');
const axios = require('axios');
const fs = require('fs');
const path = require('path');

// Configurações
const WEBHOOK_URL = 'http://localhost:5678/webhook/bf2f34f9-7412-4c66-ad62-240b56a3a8bf';
const SESSION_NAME = 'ergoanalista';
// Usar o caminho raiz do projeto, não o diretório atual
const BASE_DIR = path.resolve(path.join(__dirname, '..'));
const TOKENS_DIR = path.join(BASE_DIR, 'tokens', SESSION_NAME);
const LOG_FILE = path.join(__dirname, 'wpp-logs.txt');

// Função para registrar logs
function logMessage(message) {
  const timestamp = new Date().toISOString();
  const logEntry = `[${timestamp}] ${message}\n`;
  
  console.log(message);
  
  fs.appendFile(LOG_FILE, logEntry, (err) => {
    if (err) console.error('Erro ao salvar log:', err);
  });
}

// Garante que o diretório tokens existe
if (!fs.existsSync(TOKENS_DIR)) {
  fs.mkdirSync(TOKENS_DIR, { recursive: true });
  logMessage(`Diretório de tokens criado: ${TOKENS_DIR}`);
}

// Inicializa o cliente WPPConnect
wppconnect
  .create({
    session: SESSION_NAME,
    headless: true,
    useChrome: false,
    puppeteerOptions: {
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    },
    catchQR: (base64Qrimg, asciiQR, attempts) => {
      logMessage('\n\n=== QR CODE - ESCANEIE COM WHATSAPP ===');
      logMessage(asciiQR);
      logMessage('==========================================');
      
      // Salva QR code como imagem para acesso fácil
      const qrCodePath = path.join(__dirname, 'qrcode.png');
      const qrImageData = base64Qrimg.replace(/^data:image\/png;base64,/, '');
      fs.writeFileSync(qrCodePath, Buffer.from(qrImageData, 'base64'));
      logMessage(`QR Code salvo em: ${qrCodePath}`);
      
      if (attempts >= 3) {
        logMessage('Muitas tentativas de leitura do QR Code. Reinicie o aplicativo.');
      }
    },
    statusFind: (statusSession) => {
      logMessage(`Status da sessão: ${statusSession}`);
    }
  })
  .then((client) => start(client))
  .catch((error) => {
    logMessage(`❌ Erro ao inicializar cliente: ${error.message}`);
    if (error.stack) logMessage(error.stack);
  });

/**
 * Inicia o cliente e configura os handlers de mensagens
 * @param {Object} client - Cliente WPPConnect inicializado
 */
function start(client) {
  logMessage('✅ WhatsApp conectado! Aguardando mensagens...');
  
  client.onMessage(async (message) => {
    if (!message.isGroupMsg) {
      logMessage(`📩 Mensagem recebida de: ${message.from}`);
      logMessage(`📝 Conteúdo: ${message.body}`);
      logMessage(`📤 Enviando para n8n...`);
      
      // Dados a serem enviados para o webhook
      const webhookData = {
        body: {
          messageType: message.type,
          text: message.body,
          from: message.from,
          chatId: message.chatId,
          pushname: message.sender.pushname || 'Usuário'
        }
      };
      
      try {
        // Envia a mensagem para o webhook (n8n)
        logMessage(`Enviando para webhook: ${JSON.stringify(webhookData)}`);
        const response = await axios.post(WEBHOOK_URL, webhookData, {
          headers: {
            'Content-Type': 'application/json'
          },
          timeout: 30000 // 30 segundos de timeout
        });
        
        logMessage(`Resposta do webhook: ${JSON.stringify(response.data)}`);
        
        // Processa a resposta
        if (response.data && response.data.message) {
          await client.sendText(message.from, response.data.message);
          logMessage('✅ Resposta enviada ao usuário');
        } else {
          // Fallback para quando não há resposta específica
          logMessage('⚠️ Webhook não retornou uma mensagem válida');
          await client.sendText(
            message.from, 
            'Recebemos sua mensagem e estamos processando. Aguarde um momento, por favor.'
          );
        }
      } catch (error) {
        logMessage(`❌ Erro ao comunicar com webhook: ${error.message}`);
        
        if (error.response) {
          // O servidor respondeu com status fora do intervalo 2xx
          logMessage(`Status: ${error.response.status}`);
          logMessage(`Dados: ${JSON.stringify(error.response.data)}`);
        } else if (error.request) {
          // A requisição foi feita mas não houve resposta
          logMessage('Sem resposta do servidor');
        }
        
        // Envia mensagem de erro para o usuário
        await client.sendText(
          message.from, 
          'Desculpe, estamos com dificuldades técnicas. Sua mensagem foi recebida, mas não pudemos processá-la no momento. Tente novamente em alguns instantes.'
        );
      }
    }
  });
  
  // Manipulador de desconexão
  client.onStateChange((state) => {
    logMessage(`Estado da conexão: ${state}`);
    if (state === 'CONFLICT' || state === 'UNPAIRED') {
      logMessage('Sessão encerrada ou conflito detectado. Reiniciando...');
      client.useHere();
    }
  });
  
  // Detecta erros e tenta reconectar
  client.onIncomingCall(async (call) => {
    logMessage(`Chamada recebida de ${call.peerJid}`);
    await client.sendText(
      call.peerJid,
      'Desculpe, não posso atender chamadas. Por favor, envie uma mensagem de texto.'
    );
  });
}
