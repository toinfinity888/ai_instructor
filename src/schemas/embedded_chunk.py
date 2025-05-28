from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class EmbeddedChunk(BaseModel):
    id: str
    content: str
    embedding: list[float]
    source: str # 'forum', 'pdf'
    url: Optional[str] = None
    page: Optional[int] = None  # only for PDF
    post_title: Optional[str] = None
    metadata: Optional[dict] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    content_hash: str