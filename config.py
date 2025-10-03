import os
from dotenv import load_dotenv

# загружаем переменные из .env
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")

# адрес сервера для ссылок
SERVER_URL = os.getenv("SERVER_URL", "http://127.0.0.1:8080")
