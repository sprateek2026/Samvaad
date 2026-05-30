import os
from dotenv import dotenv_values

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_env = dotenv_values(os.path.join(BASE_DIR, ".env"))

FIREBASE_CREDENTIALS_PATH = _env.get("FIREBASE_CREDENTIALS_PATH", os.path.join(BASE_DIR, "firebase-credentials.json"))
_db_path = _env.get("DATABASE_PATH", os.path.join(BASE_DIR, "data", "samvaad.db"))
DATABASE_PATH = _db_path if os.path.isabs(_db_path) else os.path.join(BASE_DIR, _db_path)
UPLOAD_DIR = _env.get("UPLOAD_DIR", os.path.join(BASE_DIR, "uploads"))
OLLAMA_MODEL = _env.get("OLLAMA_MODEL", "gemma3:4b")
OLLAMA_HOST = _env.get("OLLAMA_HOST", "http://localhost:11434")
MAPMYINDIA_API_KEY = _env.get("MAPMYINDIA_API_KEY", "")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
