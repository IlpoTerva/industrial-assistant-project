from api.config import settings

from mes_agent.service import stream_chat_response as mes_agent #TODO
from doc_agent.service import stream_chat_response as doc_agent

QUERY_PREFIX = "query: "

AGENTS = {"docs": doc_agent, "mes": mes_agent}
MODE_TO_AGENT = {"manual": "docs", "troubleshooting": "docs", "mes": "mes"}

MES_WORDS = ("oee", "scrap", "downtime", "order", "work center", "setup time") #NOTE add more
_model = None

def _pick_agent(mode: str, message: str):
    if mode in MODE_TO_AGENT:
        return MODE_TO_AGENT[mode]
    return "mes" if any(w in message.lower() for w in MES_WORDS) else "docs"

def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(settings.EMBEDDING_MODEL)
    return _model

def _embed_query(query: str) -> list[float]:
    model = _get_model()
    vec = model.encode(QUERY_PREFIX + query, normalize_embeddings=True)
    return vec.tolist()


