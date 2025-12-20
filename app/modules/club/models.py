from sqlalchemy import Column, Integer, String, Text
from app.core.database import Base

class BoardMember(Base):
    __tablename__ = "board_members"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    role = Column(String)
    bio = Column(String) # e.g., "Physics Major, loves spin-1/2 particles"
    image_url = Column(String, nullable=True) # Placeholder for now

class Activity(Base):
    __tablename__ = "activities"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)
    date = Column(String) # Simple string for MVP (e.g., "2025-12-01")
