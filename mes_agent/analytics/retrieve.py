
import chromadb
from sentence_transformers import SentenceTransformer
from api.config import settings
from pipelines.load_data import load_fault_codes, CODE_PATTERN 
import re



_collection = None
_model = None

def embed(texts, is_query=False):
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.EMBEDDING_MODEL)
    prefix = "query: " if is_query else "passage: "
    return _model.encode([prefix + t for t in texts], normalize_embeddings=True).tolist()

def normalize_code(s: str) -> str:
    return re.sub(r"[-_ ]", "", s.upper())

# ------------------------------------------------------------------
# Retrieval  — exact code lookup + code-filtered history + semantic
# ------------------------------------------------------------------
def get_collection():
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=settings.VECTOR_STORE_DIR)
        _collection = client.get_collection(settings.VECTOR_COLLECTION) 
    return _collection


def retrieve(query, k=5):
    col = get_collection()
    code_lookup, _ = load_fault_codes()
    codes = [normalize_code(c) for c in CODE_PATTERN.findall(query)]
    ctx = {"exact_codes": [], "code_logs": [], "semantic": []}
    q_emb = embed([query], is_query=True)

    for c in codes:
        if c in code_lookup:
            ctx["exact_codes"].append(code_lookup[c])

    if codes:
        res = col.query(
            query_embeddings=q_emb, n_results=k,
            where={"$and": [{"source_type": "log"}, {"code_norm": {"$in": codes}}]},
        )
        ctx["code_logs"] = res["documents"][0]

    res = col.query(query_embeddings=q_emb, n_results=k)
    ctx["semantic"] = res["documents"][0]
    return ctx
