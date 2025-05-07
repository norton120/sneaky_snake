import logging
import os

logger = logging.getLogger('sneaky_snake')
logger.setLevel(os.getenv('LOG_LEVEL', 'INFO').upper())
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)





