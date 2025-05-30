const wppconnect = require('@wppconnect-team/wppconnect');
const axios = require('axios');

const WEBHOOK_URL = 'http://localhost:5678/webhook/bf2f34f9-7412-4c66-ad62-240b56a3a8bf';

wppconnect
  .create({
    session: 'ergoanalista',
    catchQR: (base64Qrimg, asciiQR) => {
      console.log('QR Code disponível - escaneie com WhatsApp:');
      console.log(asciiQR);
    },
    statusFind: (statusSession, session) => {
      console.log('Status:', statusSession);
    }
  })
  .then((client) => start(client))
  .catch((error) => console.error(error));

function start(client) {
  client.onMessage(async (message) => {
    if (!message.isGroupMsg) {
      try {
        const response = await axios.post(WEBHOOK_URL, {
          body: {
            messageType: message.type,
            text: message.body,
            from: message.from,
            chatId: message.chatId
          }
        });
        
        if (response.data && response.data.message) {
          await client.sendText(message.from, response.data.message);
        }
      } catch (error) {
        console.error('Erro:', error.message);
        await client.sendText(message.from, 'Desculpe, ocorreu um erro. Tente novamente.');
      }
    }
  });
}
