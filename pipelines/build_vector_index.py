"""
Simple vector index framework for initial testing and development. This is a basic implementation that allows you to create a vector index from a set of documents and perform similarity searches.
"""
from __future__ import annotations

import sys

from pathlib import Path
from typing import Iterable, Optional, Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from api.config import settings
import re
from collections import Counter
import json

EMBED_MODEL = settings.EMBEDDING_MODEL
CHROMA_PATH = settings.VECTOR_STORE_DIR


_model = None

RAW_DIR_MANUALS = Path(settings.VECTOR_STORE_DIR).resolve().parent / "raw" / "manuals"
RAW_DIR_CASES = Path(settings.VECTOR_STORE_DIR).resolve().parent / "raw" / "troubleshoot"

# e5 prefix conventions — keep in sync with analytics/document_search.py
PASSAGE_PREFIX = "passage: "

# Approx token budget per chunk (e5 char heuristic: ~4 chars/token)
CHUNK_CHARS = 1600          # ~400 tokens
CHUNK_OVERLAP_CHARS = 240   # ~60 tokens
MIN_CHUNK_CHARS = 200       # drop fragments shorter than ~50 tokens

INDEXABLE_SUFFIXES = {".pdf", ".txt", ".md", ".docx", ".xlsx"}

SKIP_FILES = {"sample_FAQs.txt"} #NOTE in the base code not in this one


def _parse_pdf(path: Path) -> Iterable[tuple[str, Optional[int], Optional[str]]]:
    from pypdf import PdfReader
    pages = [(page.extract_text() or "") for page in PdfReader(str(path)).pages]

    def key(line: str) -> str:
        return re.sub(r"\d+", "#", line.strip())

    counts = Counter(k for t in pages for k in {key(l) for l in t.splitlines() if l.strip()})
    boiler = {k for k, n in counts.items() if n > len(pages)*0.5}

    for i, text in enumerate(pages, start=1):
        clean = "\n".join(l for l in text.splitlines() if l.strip() and key(l) not in boiler)
        if clean.strip():
            yield clean, i, None

PARSERS = {
    ".pdf": _parse_pdf,
}

def _chunk(text: str) -> list[str]:
    text = " ".join(text.split())  # normalize whitespace
    if len(text) <= CHUNK_CHARS:
        return [text] if len(text) >= MIN_CHUNK_CHARS else ([text] if text else [])

    chunks: list[str] = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + CHUNK_CHARS, n)
        # try to break on a sentence/space boundary near the end
        if end < n:
            window = text.rfind(" ", start + MIN_CHUNK_CHARS, end)
            if window != -1:
                end = window
        chunk = text[start:end].strip()
        if len(chunk) >= MIN_CHUNK_CHARS or (chunk and not chunks):
            chunks.append(chunk)
        if end >= n:
            break
        start = max(end - CHUNK_OVERLAP_CHARS, start + 1)
    return chunks



def build() -> None:
    import chromadb
    from sentence_transformers import SentenceTransformer

    if not RAW_DIR_MANUALS.exists():
        raise SystemExit(f"Raw KB directory not found: {RAW_DIR_MANUALS}")

    files = sorted(
        p for p in RAW_DIR_MANUALS.iterdir()
        if p.suffix.lower() in PARSERS and p.name not in SKIP_FILES
    )
    if not files:
        raise SystemExit(f"No indexable files in {RAW_DIR_MANUALS} (looked for {sorted(INDEXABLE_SUFFIXES)})")

    print(f"Loading embedding model: {settings.EMBEDDING_MODEL} ...")
    model = SentenceTransformer(settings.EMBEDDING_MODEL)

    ids: list[str] = []
    docs: list[str] = []
    metas: list[dict[str, Any]] = []
    per_source: dict[str, int] = {}

    for path in files:
        parser = PARSERS[path.suffix.lower()]
        chunk_index = 0
        try:
            records = list(parser(path))
        except Exception as exc:
            print(f"  ! skipping {path.name}: {exc}")
            continue
        for text, page, sheet in records:
            for chunk in _chunk(text):
                ids.append(f"{path.name}::{chunk_index}")
                docs.append(chunk)
                metas.append(
                    {
                        "source": path.name,
                        "page": page if page is not None else "",
                        "sheet": sheet if sheet is not None else "",
                        "chunk_index": chunk_index,
                    }
                )
                chunk_index += 1
        per_source[path.name] = chunk_index
        print(f"  {path.name}: {chunk_index} chunks")

    if not docs:
        raise SystemExit("No chunks produced — nothing to index.")

    print(f"Embedding {len(docs)} chunks ...")
    embeddings = model.encode(
        [PASSAGE_PREFIX + d for d in docs],
        normalize_embeddings=True,
        show_progress_bar=True,
        batch_size=32,
    )

    print(f"Persisting to Chroma at {settings.VECTOR_STORE_DIR} ...")
    client = chromadb.PersistentClient(path=settings.VECTOR_STORE_DIR)
    try:
        client.delete_collection(settings.MANUALS_COLLECTION)  # idempotent rebuild
    except Exception:
        pass
    collection = client.create_collection(
        settings.MANUALS_COLLECTION, metadata={"hnsw:space": "cosine"}
    )
    collection.add(
        ids=ids,
        embeddings=[e.tolist() for e in embeddings],
        documents=docs,
        metadatas=metas,
    )

    total = sum(per_source.values())
    print("\nDone.")
    print(f"  collection: {settings.MANUALS_COLLECTION}")
    print(f"  total chunks: {total}")
    for src, n in per_source.items():
        print(f"    - {src}: {n}")


CASES_JSON = Path(settings.CASES_JSON)
CASES_COLLECTION = settings.TROUBLE_COLLECTION
REQUIRED_KEYS = {"id", "section", "symptom", "steps"}


def _case_text(c: dict[str, Any]) -> str:
    parts = [c["section"], c.get("alarm_text", ""), c["symptom"]]
    return ". ".join(p for p in parts if p)

def build_cases() -> None:
    import chromadb
    from sentence_transformers import SentenceTransformer

    if not CASES_JSON.exists():
        raise SystemExit(f"{CASES_JSON} not found")
    
    cases = json.loads(CASES_JSON.read_text(encoding="utf-8"))
    ids = [c.get("id") for c in cases]
    if len(ids) != len(set(ids)):
        raise SystemExit("Duplicate case ids in cases.json")
    for c in cases:
        missing = REQUIRED_KEYS - c.keys()
        if missing:
            raise SystemExit(f"Cases {c.get('id')} missing keys: {missing}")

    model = SentenceTransformer(EMBED_MODEL)
    docs = [_case_text(c) for c in cases]
    embeddings = model.encode([PASSAGE_PREFIX + d for d in docs], normalize_embeddings=True)

    metas = [
        {
            "section": c["section"],
            "page": c.get("page", ""),
            "alarm_codes": ",".join(c.get("alarm_codes", []))

        }
        for c in cases
    ]

    client = chromadb.PersistentClient(path=CHROMA_PATH)
    try:
        client.delete_collection(CASES_COLLECTION)
    except Exception:
        pass
    col = client.create_collection(CASES_COLLECTION, metadata={"hnsw:space": "cosine"})
    col.add(ids=ids, embeddings=[e.tolist() for e in embeddings], documents=docs, metadatas=metas)
    print(f"  cases: {len(cases)} indexed into {CASES_COLLECTION}")

MD_COLLECTION = settings.COMMON_COLLECTION

from pipelines.load_data import load_fault_codes, load_fault_logs, load_instructions

def build_md():
    import chromadb
    from sentence_transformers import SentenceTransformer
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    try:                                   
        client.delete_collection(MD_COLLECTION)
    except Exception:
        pass
    col = client.create_collection(MD_COLLECTION, metadata={"hnsw:space": "cosine"})

    _, code_records = load_fault_codes()
    records = load_instructions() + code_records + load_fault_logs()
    if not records:
        raise SystemExit("No data found — check the paths in the Config section.")

    ids   = [r[0] for r in records]
    docs  = [r[1] for r in records]
    metas = [r[2] for r in records]

    model = SentenceTransformer(EMBED_MODEL)
    embeddings = model.encode([PASSAGE_PREFIX + d for d in docs], normalize_embeddings=True)
    col.add(ids=ids, documents=docs, metadatas=metas, embeddings=embeddings)
    print(f"Indexed {len(ids)} chunks "
          f"({sum(m['source_type']=='instruction' for m in metas)} instr, "
          f"{sum(m['source_type']=='code' for m in metas)} codes, "
          f"{sum(m['source_type']=='log' for m in metas)} logs).")

def build_all():
    build_cases()
    build()
    build_md()


def main():
    build_all()

if __name__ =="__main__":
    main()
    