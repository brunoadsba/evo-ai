from fastapi import Request, HTTPException, status
from src.config.settings import api_key_settings
import logging

logger = logging.getLogger(__name__)

async def verify_api_key(request: Request):
    """
    Middleware para verificar a validade da API key
    """
    # Verifica se o caminho da requisição é para a API do WhatsApp
    if "/api/whatsapp/" in request.url.path:
        api_key = request.headers.get("x-api-key")
        
        if not api_key:
            logger.warning(f"Requisição sem API key: {request.url.path}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key não fornecida"
            )
            
        if api_key != api_key_settings.WHATSAPP_INTEGRATION_KEY:
            logger.warning(f"API key inválida: {api_key}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )
        
        # Adiciona a informação da API key ao request para uso posterior
        request.state.api_key = api_key
    
    return True
