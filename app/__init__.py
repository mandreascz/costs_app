import logging
import os
import dotenv

env_path = os.path.join(os.path.abspath('.'), '.env')
dotenv.load_dotenv(env_path)

TESSERACT_PATH = os.getenv('TESSERACT_PATH')

logger = logging.getLogger('costs_app')
logger.setLevel(logging.DEBUG)

from .ocr import extract_text_from_image
from .parsers import ParserFactory



