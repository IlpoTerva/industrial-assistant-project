from dotenv import load_dotenv
load_dotenv()

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


def _resolve_path(value: str) -> str:
    """Resolve a possibly-relative path against the project root."""
    p = Path(value)
    return str(p if p.is_absolute() else (BASE_DIR / p))


class Settings:
    # ---- Local LLM (Ollama, OpenAI-compatible endpoint) ----
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1") #http://localhost:11434/api/chat for ollama api
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:14b-instruct")
    OLLAMA_MODEL_FALLBACK = os.getenv("OLLAMA_MODEL_FALLBACK", "qwen2.5:7b-instruct")
    
    LLM_MODELS = [OLLAMA_MODEL, OLLAMA_MODEL_FALLBACK]
    # ---- Embeddings + Vector store (all local) ----
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-base")
    VECTOR_STORE_DIR = _resolve_path(os.getenv("VECTOR_STORE_DIR", "data/chroma_store"))
    # Chroma requires a 3–512 char collection name ([a-zA-Z0-9._-]).
    MANUALS_COLLECTION = os.getenv("MANUALS_COLLECTION","manuals") 
    TROUBLE_COLLECTION = os.getenv("TROUBLE_COLLECTION","troubleshoot") 
    COMMON_COLLECTION = os.getenv("COMMON_COLLECTION", "common")

    MANUAL_IMAGES = _resolve_path(os.getenv("MANUAL_IMAGES", "data/raw/manual/figures"))

    RAG_TOP_K = int(os.getenv("RAG_TOP_K", "5"))
    RAG_SCORE_FLOOR = float(os.getenv("RAG_SCORE_FLOOR", "0.75"))
    CASES_JSON = os.getenv("TROUBLESHOOT_CASES_JSON", "data/cases.json")


    TS_MARGIN = os.getenv("TS_MARGIN", "0.05")
    TS_OPTIONS_MAX = os.getenv("TS_MAX_OPTIONS", "4")
    # ---- Agent loop ----
    MAX_TOOL_ITERS = int(os.getenv("MAX_TOOL_ITERS", "6"))

    DATA_ENDPOINT = os.getenv("DATA_ENDPOINT", "http://localhost:8000") #MES endpoint
    FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
    
    VOICE_DIR = {
        "en": _resolve_path(os.getenv("EN_DIR", "voices/en/john/medium")),
        "fi": _resolve_path(os.getenv("FI_DIR", "voices/fi/harri/medium"))
        }
    VOICE_FILE = {
        "en": os.getenv("EN_FILES", "en_US-john-medium"),
        "fi": os.getenv("FI_FILES", "fi_FI-harri-medium")
        }
    SUPPORTED_LANGUAGES = [""]
    

settings = Settings()
