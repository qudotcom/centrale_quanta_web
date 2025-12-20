from pydantic import BaseModel
from typing import Optional

# --- BOARD MEMBERS ---
class BoardMemberBase(BaseModel):
    name: str
    role: str
    bio: str
    image_url: Optional[str] = None

class BoardMemberCreate(BoardMemberBase):
    pass

class BoardMember(BoardMemberBase):
    id: int

    class Config:
        from_attributes = True

# --- ACTIVITIES ---
class ActivityBase(BaseModel):
    title: str
    description: str
    date: str

class ActivityCreate(ActivityBase):
    pass

class Activity(ActivityBase):
    id: int

    class Config:
        from_attributes = True
