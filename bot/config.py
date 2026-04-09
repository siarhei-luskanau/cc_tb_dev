import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN: str = os.environ["TELEGRAM_BOT_TOKEN"]
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "qwen3:0.6b")
AVAILABLE_MODELS: list[str] = os.getenv(
    "AVAILABLE_MODELS", "qwen3:0.6b,qwen3.5:0.8b,gpt-oss:20b"
).split(",")
