import logging
from dotenv import load_dotenv
load_dotenv()

# Setup for the general application logger
logger = logging.getLogger(__name__)
app_handler = logging.StreamHandler()
app_handler.setLevel(logging.INFO)
app_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
app_handler.setFormatter(app_formatter)
logger.addHandler(app_handler)
logger.setLevel(logging.INFO)
