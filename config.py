from dotenv import load_dotenv
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MEMORY_DICT = {}

# Загрузка переменных окружения
dotenv_path = os.path.join(BASE_DIR, ".env")


if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# Настройки телеграм
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")

# Настройка подключения openai
CHAT_GPT_TOKEN = os.environ.get("CHAT_GPT_TOKEN")
ASS_ID = os.environ.get("ASS_ID")
