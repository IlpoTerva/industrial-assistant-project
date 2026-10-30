from typing import Any, List, Literal, Optional
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    session_id: str
    mode: str = "auto"
    choice_id: Optional[str] = None


class Source(BaseModel):
    doc: str
    section: str =""
    page: Optional[int] = None

class ChatResponse(BaseModel):
    route: Optional[str] = None # what agent is answering 
    blocks: list[dict]
    sources: list[Source] = []



    