from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DocumentBase(BaseModel):
    title: str
    content: str
    source_path: Optional[str] = None


class DocumentCreate(DocumentBase):
    pass


class DocumentInDB(DocumentBase):
    id: int
    uploaded_at: str

    class Config:
        from_attributes = True


class Document(DocumentBase):
    id: int
    uploaded_at: str

    class Config:
        from_attributes = True
