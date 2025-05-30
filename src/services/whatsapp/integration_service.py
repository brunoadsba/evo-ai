import httpx
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class WhatsAppIntegrationService:
    def __init__(self, settings):
        self.evolution_api_url = settings.EVOLUTION_API_URL
        self.evolution_api_key = settings.EVOLUTION_API_KEY
        self.ergoanalist_url = settings.ERGOANALIST_API_URL

    async def process_message(self, message_data: Dict[str, Any]):
        try:
            logger.info(f"Recebendo mensagem WhatsApp: {message_data}")
            
            # Extrair informações da mensagem (Evolution API format)
            sender_phone = self._extract_phone_number(message_data)
            message_body = self._extract_message_content(message_data)
            
            if not message_body:
                logger.warning("Mensagem vazia recebida")
                return {"status": "ignored", "reason": "empty_message"}

            logger.info(f"Processando mensagem de {sender_phone}: {message_body}")

            # Consultar agente ErgoAnalista
            async with httpx.AsyncClient() as client:
                ai_response = await self._get_ai_response(client, message_body)

            # Enviar resposta via Evolution API
            await self.send_whatsapp_message(sender_phone, ai_response)
            
            return {"status": "success", "response": ai_response}
        
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")
            return {"status": "error", "message": str(e)}

    def _extract_phone_number(self, message_data: Dict[str, Any]) -> str:
        """Extract phone number from Evolution API message data"""
        # Evolution API pode usar diferentes formatos
        phone = (
            message_data.get('from') or
            message_data.get('key', {}).get('remoteJid', '').split('@')[0] or
            message_data.get('phone', '')
        )
        return phone.replace('@c.us', '').replace('@s.whatsapp.net', '')

    def _extract_message_content(self, message_data: Dict[str, Any]) -> str:
        """Extract message content from Evolution API message data"""
        # Evolution API pode usar diferentes formatos de mensagem
        message = (
            message_data.get('body') or
            message_data.get('message', {}).get('conversation') or
            message_data.get('message', {}).get('extendedTextMessage', {}).get('text') or
            message_data.get('text', '')
        )
        return message.strip()

    async def _get_ai_response(self, client, message_body):
        try:
            logger.info(f"Consultando ErgoAnalista: {message_body}")
            response = await client.post(
                self.ergoanalist_url, 
                json={"message": message_body},
                headers={"Content-Type": "application/json"},
                timeout=30.0
            )
            response.raise_for_status()
            
            result = response.json()
            ai_response = result.get('response', 'Desculpe, não entendi.')
            logger.info(f"Resposta do ErgoAnalista: {ai_response}")
            return ai_response
            
        except httpx.TimeoutException:
            logger.error("Timeout ao consultar ErgoAnalista")
            return 'Desculpe, o serviço está temporariamente indisponível.'
        except Exception as e:
            logger.error(f"Erro na API do agente: {e}")
            return 'Erro ao processar sua solicitação.'

    async def send_whatsapp_message(self, to_number: str, message: str):
        async with httpx.AsyncClient() as client:
            try:
                logger.info(f"Enviando mensagem para {to_number}")
                
                response = await client.post(
                    f"{self.evolution_api_url}/message/sendText/ergo-analista",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.evolution_api_key}"
                    },
                    json={
                        "number": to_number,
                        "options": {"delay": 1000},
                        "textMessage": {"text": message}
                    },
                    timeout=10.0
                )
                response.raise_for_status()
                logger.info(f"Mensagem enviada com sucesso para {to_number}")
                
            except httpx.TimeoutException:
                logger.error(f"Timeout ao enviar mensagem para {to_number}")
            except Exception as e:
                logger.error(f"Erro ao enviar mensagem para {to_number}: {e}")
