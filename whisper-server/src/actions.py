import unidecode
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

keywords = ['prender', 'apagar', 'alexa', 'unknown']

def find_any_keywords(text):
    """
    Busca palabras clave en el texto y devuelve el comando correspondiente
    """
    text = text.lower().strip()
    
    # Buscar cualquier keyword en el texto
    for keyword in keywords:
        if keyword in text:
            logger.info(f"Palabra clave encontrada: {keyword}")
            return keyword

    logger.info(f"No se encontró ninguna palabra clave en el texto: {text}")
    return 'None'

def set_command(command):
    """
    Convierte comandos de texto a valores hexadecimales
    """
    commands = {
        "TURN_ON": "0501",
        "TURN_OFF": "0500",
        "UNKNOWN": "0000"
    }
    
    try:
        hex_command = commands.get(command, 0x0000)
        return {
            "command": hex_command,
            "status": "success" if command != "UNKNOWN" else "ignored"
        }
    except Exception as e:
        return {
            "command": 0x0000,
            "status": "error",
            "error": str(e)
        }

