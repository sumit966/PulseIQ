import os
from dotenv import load_dotenv

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "dummy").lower()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "openai/gpt-oss-20b")
USE_LLM = os.getenv("USE_LLM", "false").lower() == "true"

DB_PATH = "data/pulseiq.db"
KAFKA_TOPIC = "pulseiq-events"
KAFKA_GROUP = "pulseiq-consumers"

