from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class TournamentMatch(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    
    # Tournament Structure
    round_number = Column(Integer, default=1) # 1 = Round of 16, 2 = Quarter finals, etc.
    next_match_id = Column(Integer, ForeignKey("matches.id"), nullable=True)
    
    # Players (Linked to Auth Module)
    player1_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    player2_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    winner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Game State
    is_active = Column(Boolean, default=True) # False when game is over
    board_state = Column(Text, default="") # Stores the Quantum FEN/JSON string
    
    # Relationships for easy access in templates
    player1 = relationship("app.modules.auth.models.User", foreign_keys=[player1_id])
    player2 = relationship("app.modules.auth.models.User", foreign_keys=[player2_id])
    winner = relationship("app.modules.auth.models.User", foreign_keys=[winner_id])
    next_match = relationship("TournamentMatch", remote_side=[id])
