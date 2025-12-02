import random
from sqlalchemy.orm import Session
from app.modules.tournament.models import TournamentMatch
from app.modules.auth.models import User

def generate_single_elimination(db: Session):
    # 1. Fetch all users who are NOT board members (assuming board members organize)
    # Or just fetch everyone. Let's fetch everyone for now.
    players = db.query(User).all()
    
    # 2. Validation: We need an even number of players
    if len(players) < 2:
        return {"error": "Not enough players to start."}
    if len(players) % 2 != 0:
        return {"error": "Need an even number of participants (Quantum limitation: pairs required)."}

    # 3. Clear old matches (Optional: for a clean restart)
    db.query(TournamentMatch).delete()
    
    # 4. Randomize
    random.shuffle(players)

    # 5. Create Matches
    matches = []
    # Loop through list with step 2 (0 vs 1, 2 vs 3, etc.)
    for i in range(0, len(players), 2):
        match = TournamentMatch(
            round_number=1,
            player1_id=players[i].id,
            player2_id=players[i+1].id,
            board_state="INITIAL_QUANTUM_STATE", # We will define this later
            is_active=True
        )
        db.add(match)
        matches.append(match)
    
    db.commit()
    return {"success": True, "matches_created": len(matches)}
