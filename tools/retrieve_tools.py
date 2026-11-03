
from typing import Any
from pathlib import Path
import json

from api.config import settings
from pipelines.load_data import load_fault_codes, CODE_PATTERN 
import re



_collections = {}
_model = None

QUERY_PREFIX = "query: "

def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(settings.EMBEDDING_MODEL)
    return _model

def _get_collection(name: str):
    if name not in _collections:
        import chromadb
        client = chromadb.PersistentClient(path=settings.VECTOR_STORE_DIR)
        _collections[name] = client.get_collection(name) 
    return _collections[name]


def _embed_query(query: str) -> list[float]:
    model = _get_model()
    vec = model.encode(QUERY_PREFIX + query, normalize_embeddings=True)
    return vec.tolist()

def normalize_code(s: str) -> str:
    return re.sub(r"[-_ ]", "", s.upper())

# Retrieve data from fault_reference.md file.

def retrieve_common(query, k=5):
    try:
        col = _get_collection(settings.COMMON_COLLECTION)
    except Exception:
        return {
            "query": query,
            "chunks": [],
            "message": ("The document index has not been built yet")
        }

    code_lookup, _ = load_fault_codes()
    codes = [normalize_code(c) for c in CODE_PATTERN.findall(query)]
    ctx = {"exact_codes": [], "code_logs": [], "semantic": []}

    for c in codes:
        if c in code_lookup:
            ctx["exact_codes"].append(code_lookup[c])

    if codes:
        res = col.query(
            query_embeddings=[_embed_query(query)], n_results=k,
            where={"$and": [{"source_type": "log"}, {"code_norm": {"$in": codes}}]},
        )
        ctx["code_logs"] = res["documents"][0]

    res = col.query(query_embeddings=[_embed_query(query=query)], n_results=k)
    ctx["semantic"] = res["documents"][0]
    return ctx


def retrieve_manuals(query):
    top_k = settings.RAG_TOP_K

    try:
        collection = _get_collection(settings.MANUALS_COLLECTION)
    except Exception:
        return {
            "query": query,
            "chunks": [],
            "source": [],
            "message": (
                "The document index has not been built yet."
                "Run: python main.py --build"
            )
        }
    try:
        res = collection.query(
            query_embeddings=[_embed_query(query)],
            n_results=top_k
        )
    except Exception as exc:
        return {"query": query, "chunks": [], "source": [], "message": f"Retrieval error {exc}"}

    documents = (res.get("documents") or [[]])[0]
    metadatas = (res.get("metadatas") or [[]])[0]
    distances = (res.get("distances") or [[]])[0]
    #related_figures = figure_retrieval(res)
    chunks: list[dict[str, Any]] = []
    for doc, md, dist in zip(documents, metadatas, distances):
        md = md or {}
        chunks.append(
            {
                "text": doc,
                "source": md.get("source"),
                "page": md.get("page"),
                "sheet": md.get("sheet"),
                "score": round(1.0 - float(dist), 4),
            })
    sources = sorted({c["source"] for c in chunks if c.get("source")})
    
    return {"query": query, "chunks": chunks, "sources": sources}


# ---- TROUBLESHOOT ALARMS; FAULTS, from real manual -----

ALARM_RE = re.compile(r"\b(?:\d{4,6}|[AF]\d{2,5}\b)")
TROUBLE_WORDS = ("error", "alarm", "fault", "vika", "hälytys", "virhe")

def _normalize_code(code: str)->str:
    return code.upper().lstrip("0")

def _load_cases(path: str):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    cases = {c["id"]: c for c in data}
    alarm_index = {}
    for c in data:
        for code in c.get("alarm_codes", []):
            alarm_index.setdefault(_normalize_code(code), []).append(c["id"])
    return  cases, alarm_index

CASES, ALARMS = _load_cases(settings.CASES_JSON)

def retrieve_case(query, exclude):
    top_k = settings.RAG_TOP_K
    exclude = exclude or set()
    base = {"query": query, "candidates": []}

    codes = {_normalize_code(c) for c in ALARM_RE.findall(query)}
    hit_ids = [cid for c in codes for cid in ALARMS.get(c, []) if cid not in exclude]
    hit_ids = list(dict.fromkeys(hit_ids))
    if hit_ids:
        return {
            **base, "match": "alarm_code", "codes": codes,
            "candidates": [CASES[cid] for cid in hit_ids]
        }
    try:
        collection = _get_collection(settings.TROUBLE_COLLECTION)
    except Exception:
        return {
            **base, "match": "none",
            "message": "Troubleshooting index not built. Run: python main.py --build"
        }
    
    try:
        res = collection.query(
            query_embeddings=[_embed_query(query)],
            n_results=top_k
        )
    except Exception as exc:
        return {**base, "match":"none", "message": f"Retrieval error {exc}"}

    scored = [(cid, round(1 - float(d), 4)) 
              for cid, d in zip(res["ids"][0], res["distances"][0]) 
              if cid not in exclude and cid in CASES]
    if not scored or scored[0][1] < settings.RAG_SCORE_FLOOR:
        return {**base, "match":"none"}
    
    top = scored[0][1]
    close = [{**CASES[cid], "score": s} for cid, s in  scored if s >= top - float(settings.TS_MARGIN)]
    return {**base, "match": "symptom", "candidates": close[:int(settings.TS_OPTIONS_MAX)]}
