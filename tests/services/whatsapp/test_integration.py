import pytest
from unittest.mock import MagicMock, patch
import json

# Supondo que temos um serviço de integração WhatsApp na seguinte localização
from src.services.whatsapp.integration_service import WhatsAppIntegrationService
from src.services.whatsapp.webhook_handler import WebhookHandler


class TestWhatsAppIntegration:
    """Testes para a integração do WhatsApp."""
    
    @pytest.fixture
    def whatsapp_service(self):
        """Fixture para criar uma instância do serviço de integração do WhatsApp."""
        return WhatsAppIntegrationService()
    
    @pytest.fixture
    def webhook_handler(self):
        """Fixture para criar uma instância do handler de webhook."""
        return WebhookHandler()
    
    @patch('src.services.whatsapp.integration_service.requests.post')
    def test_send_message(self, mock_post, whatsapp_service):
        """Testa o envio de mensagem para o WhatsApp."""
        # Configurar o mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_post.return_value = mock_response
        
        # Executar o método a ser testado
        result = whatsapp_service.send_message(
            phone_number="5571999999999",
            message="Teste de mensagem"
        )
        
        # Verificar o resultado
        assert result["success"] is True
        mock_post.assert_called_once()
    
    def test_process_webhook_message(self, webhook_handler):
        """Testa o processamento de uma mensagem recebida via webhook."""
        # Criar uma mensagem de exemplo
        webhook_data = {
            "body": {
                "messageType": "chat",
                "text": "Olá, como vai?",
                "from": "5571999999999@c.us",
                "chatId": "5571999999999@c.us",
                "pushname": "Usuário Teste"
            }
        }
        
        # Processar a mensagem
        with patch('src.services.whatsapp.webhook_handler.process_message') as mock_process:
            mock_process.return_value = {"message": "Resposta processada"}
            result = webhook_handler.handle_webhook(webhook_data)
            
            # Verificar se o método foi chamado com os parâmetros corretos
            mock_process.assert_called_with(
                text="Olá, como vai?",
                sender="5571999999999@c.us",
                push_name="Usuário Teste"
            )
            
            # Verificar o resultado
            assert result == {"message": "Resposta processada"}
