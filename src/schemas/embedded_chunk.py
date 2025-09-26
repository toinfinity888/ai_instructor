from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class EmbeddedChunk(BaseModel):
    id: str
    section: Optional[str] = None
    subsection: Optional[str] = None
    question: Optional[str] = None
    content: str
    embedding: Optional[list[float]] = None
    url: Optional[str] = None
    filename: Optional[str] = None
    page: Optional[int] = None  # only for PDF
    created_at: datetime = Field(default_factory=datetime.utcnow)
    content_hash: str
    file_type: Optional[str] = None