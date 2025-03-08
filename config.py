import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Configuration
DERIBIT_API_KEY = os.getenv('DERIBIT_API_KEY', '')
DERIBIT_API_SECRET = os.getenv('DERIBIT_API_SECRET', '')

BITMEX_API_KEY = os.getenv('BITMEX_API_KEY', '')
BITMEX_API_SECRET = os.getenv('BITMEX_API_SECRET', '')

BYBIT_API_KEY = os.getenv('BYBIT_API_KEY', '')
BYBIT_API_SECRET = os.getenv('BYBIT_API_SECRET', '')