# app/utils/pagination.py
# Member 4 - Pagination logic for GET /api/students/

import math
from typing import TypeVar
from sqlalchemy.orm import Query
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    page:      int = Field(default=1,  ge=1,        description="Page number (1-based)")
    page_size: int = Field(default=10, ge=1, le=100, description="Items per page")


def paginate_query(query: Query, page: int, page_size: int) -> tuple[list, int]:
    """
    Execute a paginated query.

    Args:
        query:     A SQLAlchemy query (filters already applied).
        page:      1-based page number.
        page_size: Number of records per page.

    Returns:
        (items, total) - the slice of ORM objects and the total row count.
    """
    total: int = query.count()
    offset = (page - 1) * page_size
    items = query.offset(offset).limit(page_size).all()
    return items, total


def calc_pages(total: int, page_size: int) -> int:
    """Return total number of pages."""
    if page_size <= 0:
        return 0
    return math.ceil(total / page_size)
