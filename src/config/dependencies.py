from fastapi import Depends
from src.config/settings import WhatsAppSettings
from src.services.whatsapp.integration_service import WhatsAppIntegrationService

def get_whatsapp_service(
    settings: WhatsAppSettings = Depends()
) -> WhatsAppIntegrationService:
    return WhatsAppIntegrationService(settings)
