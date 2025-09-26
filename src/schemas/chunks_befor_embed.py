from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import hashlib

class ChunksBeforeEmbed(BaseModel):
    id: str
    section: str
    subsection: Optional[str] = None
    question: Optional[str] = None
    content: Optional[str] = None
    url: str
    filename: Optional[str] = None
    page: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    content_hash: Optional[str] = None
    file_type: Optional[str] = None
    
    def update_content_hash(self):
        if self.content:
            self.content_hash = hashlib.sha256(self.content.encode()).hexdigest()

    @field_validator('content_hash', mode='before')
    @classmethod
    def fill_content_hash(cls, v, values):
        if not v and (content := values.get('content')):
            return hashlib.sha256(content.encode()).hexdigest()
        return v
    