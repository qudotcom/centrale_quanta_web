from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Text, Float, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
import datetime
import time

class TournamentMatch(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    tournament_id = Column(String, index=True) # Groups matches into one event
    round_number = Column(Integer, default=1)
    
    # Linking Logic
    next_match_id = Column(Integer, nullable=True) # ID of the match the winner goes to
    next_match_slot = Column(Integer, nullable=True) # 1 or 2 (Player 1 or Player 2 slot)

    # Players
    player1_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    player2_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    winner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Game State
    is_active = Column(Boolean, default=True)
    board_state = Column(Text, default="") 
    current_turn = Column(String, default="white") 
    ai_difficulty = Column(String, default="normal") 

    # Timer
    p1_time_left = Column(Float, default=600.0)
    p2_time_left = Column(Float, default=600.0)
    last_move_timestamp = Column(Float, default=lambda: time.time())
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    player1 = relationship("app.modules.auth.models.User", foreign_keys=[player1_id])
    player2 = relationship("app.modules.auth.models.User", foreign_keys=[player2_id])
    winner = relationship("app.modules.auth.models.User", foreign_keys=[winner_id])
