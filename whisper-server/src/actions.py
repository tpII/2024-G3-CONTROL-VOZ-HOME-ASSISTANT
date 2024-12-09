import unidecode
import logging

# Configurar logging
logging.basicConfig(
    filename='./log/actions.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

commands = {
    'prender': 0x0501,
    'apagar': 0x0500,
    'alexa': 0x0502,
    'None': 0x0000,
}

keywords = ['prender', 'apagar', 'alexa']

def __find_any_keywords(text):
    """
    Busca palabras clave en el texto y devuelve el comando correspondiente
    """
    text = text.lower()
    
    # Buscar cualquier keyword en el texto
    for keyword in keywords:
        if keyword in text:
            logger.info(f"Palabra clave encontrada: {keyword}")
            return keyword

    logger.info(f"No se encontró ninguna palabra clave en el texto: {text}")
    return 'None'

def set_command(text):
    """
    Determina el comando basado en el texto transcrito
    """
    keyword = __find_any_keywords(text)
    return {
        "command": commands[keyword],
        "keyword": keyword,
        "original_text": text
    }

