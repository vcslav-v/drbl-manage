"""Pydantic's models."""
from pydantic import BaseModel


class Task(BaseModel):
    """Task model."""
    id: int
    link: str
    targ_like: int
    done_like: int


class LikerPage(BaseModel):
    """Liker page model."""
    total_accounts: int
    in_work_accs: int
    target_accounts: int
    tasks: list[Task]
