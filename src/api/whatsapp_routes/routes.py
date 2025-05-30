from fastapi import APIRouter, Request, Depends
from src.services.whatsapp.integration_service import WhatsAppIntegrationService
from src.config.settings import WhatsAppSettings

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])

def get_whatsapp_settings() -> WhatsAppSettings:
    return WhatsAppSettings()

def get_whatsapp_service(
    settings: WhatsAppSettings = Depends(get_whatsapp_settings)
) -> WhatsAppIntegrationService:
    return WhatsAppIntegrationService(settings)

@router.post("/webhook")
async def receive_whatsapp_message(
    request: Request,
    service: WhatsAppIntegrationService = Depends(get_whatsapp_service)
):
    """
    Webhook para receber mensagens do WhatsApp via Evolution API
    """
    # Receber payload da Evolution API
    payload = await request.json()
    
    # Processar mensagem
    result = await service.process_message(payload)
    
    return result

@router.get("/status")
async def whatsapp_status():
    """
    Verificar status da integração WhatsApp
    """
    return {
        "status": "active",
        "service": "WhatsApp Integration",
        "webhook_endpoint": "/whatsapp/webhook"
    }
