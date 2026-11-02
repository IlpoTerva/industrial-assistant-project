from pathlib import Path
import re
import csv

DATA_DIR = Path("data")
INSTRUCTIONS_DIR = DATA_DIR / "raw/common/sop_assembly"       # .md / .txt files
FAULT_CODES_FILE = DATA_DIR / "processed/fault_code_master.csv"    # code, description, action
FAULT_LOGS_FILE  = DATA_DIR / "raw/common/fault_reference"     # date, machine, code, symptom, action_taken, resolution

CODE_PATTERN = re.compile(r"\b([A-Z]{1,4}[-_ ]?\d{2,6})\b")


def normalize_code(s: str) -> str:
    return re.sub(r"[-_ ]", "", s.upper())

def split_markdown(text):
    if re.search(r"(?m)^#{1,6}\s", text):
        chunks = re.split(f"\n(?=#{1,6}\s)", text)
    else:
        chunks = text.split("\n\n")
    #drop heading only and empty chunks
    return [c.strip() for c in chunks if c.strip() and "\n" in c.strip()]


def _iter_files(path, exts=(".md", ".txt")):
    p = Path(path)
    if p.is_file():
        return [p]
    if p.is_dir():
        return [f for f in sorted(p.rglob("*")) if f.suffix.lower() in exts]
    for ext in exts:                      # bare stem, e.g. .../sop_assembly -> .../sop_assembly.md
        if p.with_suffix(ext).is_file():
            return [p.with_suffix(ext)]
    print(f"[warn] no files found at {p.resolve()}")
    return []



def load_instructions():
    records = []
    for fp in _iter_files(INSTRUCTIONS_DIR):
        text = fp.read_text(encoding="utf-8")
        #chunks = re.split(r"\n(?=#{1,6}\s)", text) if "#" in text else text.split("\n\n")
        chunks = split_markdown(text)
        for i, ch in enumerate(c.strip() for c in chunks):
            if ch:
                records.append((f"instr::{fp.stem}::{i}", ch,
                                {"source_type": "instruction", "file": fp.name}))
    return records

def load_fault_logs():
    records = []
    for fp in _iter_files(FAULT_LOGS_FILE):
        text = fp.read_text(encoding="utf-8")
        #chunks = re.split(r"\n(?=#{1,6}\s)", text) if "#" in text else text.split("\n\n")
        chunks = split_markdown(text)
        for i, ch in enumerate(c.strip() for c in chunks):
            if not ch:
                continue
            found = CODE_PATTERN.findall(ch)
            code = found[0].upper() if found else ""
            records.append((f"log::{fp.stem}::{i}", ch,
                            {"source_type": "log", "file": fp.name,
                             "code": code, "code_norm": normalize_code(code) if code else ""}))
    return records

def load_fault_codes():
    """Returns (exact_lookup_dict, vector_records). Codes are BOTH exact-lookup
    keys and indexed, so 'temperature sensor fault' can surface them semantically too."""
    lookup, records = {}, []
    if not FAULT_CODES_FILE.exists():
        return lookup, records
    with open(FAULT_CODES_FILE, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            code = row["fault_code"].strip().upper()
            lookup[normalize_code(code)] = row
            text = (f"Fault code {code}: {row.get('category','')}. ")
            records.append((
                f"code::{code}", text,
                {"source_type": "code", "code": code, "code_norm": normalize_code(code)},
            ))
    return lookup, records

