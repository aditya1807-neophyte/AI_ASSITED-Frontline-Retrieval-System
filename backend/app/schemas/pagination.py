"""
Pydantic schemas for pagination.

Phase 3 — Pagination schema definitions.
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel as _BaseModel


T = TypeVar('T')


class Page(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    pages: int


class PageWithMeta(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    pages: int
    has_next: bool
    has_prev: bool
