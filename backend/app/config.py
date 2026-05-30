import os
from dotenv import dotenv_values

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_env = dotenv_values(os.path.join(BASE_DIR, ".env"))


def _cfg(key, default=None):
    # Real environment variables (e.g. set in the Railway/host dashboard) take
    # precedence, then the local .env file, then the default. dotenv_values()
    # alone does NOT read os.environ, so deployed env vars would be ignored.
    val = os.environ.get(key)
    if val is None:
        val = _env.get(key)
    return val if val is not None else default


FIREBASE_CREDENTIALS_PATH = _cfg("FIREBASE_CREDENTIALS_PATH", os.path.join(BASE_DIR, "firebase-credentials.json"))
_db_path = _cfg("DATABASE_PATH", os.path.join(BASE_DIR, "data", "samvaad.db"))
DATABASE_PATH = _db_path if os.path.isabs(_db_path) else os.path.join(BASE_DIR, _db_path)
UPLOAD_DIR = _cfg("UPLOAD_DIR", os.path.join(BASE_DIR, "uploads"))
OLLAMA_MODEL = _cfg("OLLAMA_MODEL", "gemma3:4b")
OLLAMA_HOST = _cfg("OLLAMA_HOST", "http://localhost:11434")
MAPMYINDIA_API_KEY = _cfg("MAPMYINDIA_API_KEY", "")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
