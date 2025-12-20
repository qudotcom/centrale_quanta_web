import random
import uuid
from sqlalchemy.orm import Session
from app.modules.tournament.models import TournamentMatch
from app.modules.auth.models import User

def generate_single_elimination(db: Session):
    """
    Generates a linked tournament bracket.
    Does NOT delete old games (History is kept).
    """
    players = db.query(User).filter(User.username != "CPU_AI").all()
    if len(players) < 2: return {"error": "Need at least 2 players."}
    
    # Generate unique Tournament ID
    tourney_id = str(uuid.uuid4())[:8]
    random.shuffle(players)

    # Determine Bracket Size (nearest power of 2)
    # Simple implementation: Just pair them up for Round 1
    # Note: Full binary tree generation is complex, this is a simplified 1-round setup
    # checking for even numbers.
    
    matches = []
    
    # Create Matches
    # For a scalable system, you'd build a binary tree.
    # Here we just create Round 1 pairs. 
    # If you want progression, we need empty matches for Round 2.
    
    # 1. Create Round 1 Matches
    round1_matches = []
    for i in range(0, len(players), 2):
        if i+1 < len(players):
            m = TournamentMatch(
                tournament_id=tourney_id,
                round_number=1,
                player1_id=players[i].id,
                player2_id=players[i+1].id,
                board_state="",
                is_active=True,
                current_turn="white"
            )
            db.add(m)
            round1_matches.append(m)
    
    db.flush() # Get IDs
    
    # 2. Create Round 2 (Finals/Semis) placeholders if needed
    # (Simplified: If 2 matches in R1, create 1 match in R2)
    if len(round1_matches) >= 2:
        for i in range(0, len(round1_matches), 2):
            if i+1 < len(round1_matches):
                # Create Next Round Match (Empty Players)
                next_m = TournamentMatch(
                    tournament_id=tourney_id,
                    round_number=2,
                    player1_id=None, # Waiting for winner
                    player2_id=None,
                    board_state="",
                    is_active=False # Inactive until filled
                )
                db.add(next_m)
                db.flush()
                
                # Link R1 matches to R2
                m1 = round1_matches[i]
                m2 = round1_matches[i+1]
                
                m1.next_match_id = next_m.id
                m1.next_match_slot = 1
                
                m2.next_match_id = next_m.id
                m2.next_match_slot = 2

    db.commit()
    return {"success": True, "tournament_id": tourney_id}
