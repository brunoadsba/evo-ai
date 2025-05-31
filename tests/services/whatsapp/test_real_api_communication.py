import requests
import json
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_real_api_communication():
    """
    Testar a comunicação real com a API externa do ErgoAnalista.
    """
    # Configurações da API externa
    url = "https://api-evoai.evoapicloud.com/api/v1/a2a/6468417b-cc79-4aed-92f5-1c57203fed8a"
    api_key = "evo_whatsapp_integration_2024"

    # Payload de teste simulando uma mensagem do WhatsApp
    payload = {
        "messageType": "text",
        "text": "Mensagem de teste de comunicação real",
        "from": "5511999999999", # Número fictício para o teste
        "chatId": "5511999999999@c.us", # ID do chat fictício para o teste
        "pushname": "Teste Real"
    }

    # Cabeçalhos necessários para a requisição
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key
    }

    logger.info(f"Tentando conectar com: {url}")
    logger.info(f"Usando API Key: {api_key}")
    logger.info(f"Enviando Payload: {json.dumps(payload, indent=2)}")

    try:
        # Enviar a requisição HTTP POST real
        response = requests.post(
            url,
            data=json.dumps(payload),
            headers=headers,
            timeout=15 # Aumentar o tempo limite para 15 segundos
        )

        # Registrar detalhes da resposta
        logger.info(f"Status Code Recebido: {response.status_code}")
        logger.info(f"Headers da Resposta: {response.headers}")
        logger.info(f"Corpo da Resposta: {response.text}")

        # Levantar um erro para códigos de status HTTP de erro (4xx ou 5xx)
        response.raise_for_status()

        logger.info("Requisição bem-sucedida!")
        return {
            "success": True,
            "status_code": response.status_code,
            "response_body": response.json() if response.text else "No response body"
        }

    except requests.exceptions.HTTPError as http_err:
        logger.error(f"Erro HTTP: {http_err}")
        return {
            "success": False,
            "error_type": "HTTP Error",
            "error_message": str(http_err),
            "status_code": response.status_code if 'response' in locals() else 'N/A',
            "response_body": response.text if 'response' in locals() else 'N/A'
        }
    except requests.exceptions.ConnectionError as conn_err:
        logger.error(f"Erro de Conexão: {conn_err}")
        return {
            "success": False,
            "error_type": "Connection Error",
            "error_message": str(conn_err)
        }
    except requests.exceptions.Timeout as time_err:
        logger.error(f"Erro de Timeout: {time_err}")
        return {
            "success": False,
            "error_type": "Timeout Error",
            "error_message": str(time_err)
        }
    except requests.exceptions.RequestException as req_err:
        logger.error(f"Outro Erro: {req_err}")
        return {
            "success": False,
            "error_type": "Request Error",
            "error_message": str(req_err)
        }
    except Exception as e:
        logger.error(f"Ocorreu um erro inesperado: {e}")
        return {
            "success": False,
            "error_type": "Unexpected Error",
            "error_message": str(e)
        }

# Executar o teste
resultado_teste_real = test_real_api_communication()
print("\n--- Resultado Final do Teste ---")
print(json.dumps(resultado_teste_real, indent=2))
