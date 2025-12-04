from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pydantic import BaseModel
import random
import time

from app.core import database, security
from app.modules.tournament import logic, models
from app.modules.auth.models import User 
from app.modules.tournament.engine import QuantumEngine, get_board_state
# Import our new AI
from app.modules.tournament.ai import QuantumAI

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

class MoveRequest(BaseModel):
    move_str: str

# --- VS MACHINE ENDPOINT ---
@router.post("/practice")
def start_practice_match(request: Request, db: Session = Depends(database.get_db)):
    """
    Creates a game: Current User vs 'CPU_AI'.
    """
    # 1. Ensure the CPU user exists
    cpu_user = db.query(User).filter(User.username == "CPU_AI").first()
    if not cpu_user:
        cpu_user = User(username="CPU_AI", email="ai@quanta.system", hashed_password="x")
        db.add(cpu_user)
        db.commit()

    # 2. Determine who the human is
    # Using the cookie middleware we added earlier
    user_data = request.state.user
    if user_data:
        human = db.query(User).filter(User.username == user_data['username']).first()
    else:
        # If not logged in, create/use a Guest account
        human = db.query(User).filter(User.username == "Guest").first()
        if not human:
            human = User(username="Guest", email="guest@temp.com", hashed_password="x")
            db.add(human)
            db.commit()

    # 3. Create the Match (Human = White/Player1, CPU = Black/Player2)
    match = models.TournamentMatch(
        round_number=0, # 0 indicates Practice/Exhibition
        player1_id=human.id,
        player2_id=cpu_user.id,
        board_state="",
        is_active=True
    )
    db.add(match)
    db.commit()
    db.refresh(match)

    return RedirectResponse(url=f"/tournament/play/{match.id}", status_code=302)


# --- EXISTING ENDPOINTS (Updated Move Logic) ---

@router.post("/seed")
def seed_participants(db: Session = Depends(database.get_db)):
    dummy_names = ["Schrodinger", "Heisenberg", "Planck", "Bohr"]
    count = 0
    for name in dummy_names:
        if not db.query(User).filter(User.username == name).first():
            user = User(username=name, email=f"{name}@q.com", hashed_password="x")
            db.add(user)
            count += 1
    db.commit()
    return RedirectResponse(url="/tournament/bracket", status_code=302)

@router.get("/bracket")
def view_bracket(request: Request, db: Session = Depends(database.get_db)):
    matches = db.query(models.TournamentMatch).filter(models.TournamentMatch.round_number > 0).all()
    player_count = db.query(User).count()
    warning = "Need even number of players." if player_count % 2 != 0 else None
    
    return templates.TemplateResponse("tournament/bracket.html", {
        "request": request, "matches": matches, "warning": warning
    })

@router.post("/generate")
def start_tournament(db: Session = Depends(database.get_db)):
    logic.generate_single_elimination(db)
    return RedirectResponse(url="/tournament/bracket", status_code=302)

@router.get("/play/{match_id}")
def play_match(match_id: int, request: Request, db: Session = Depends(database.get_db)):
    match = db.query(models.TournamentMatch).filter(models.TournamentMatch.id == match_id).first()
    if not match: return RedirectResponse(url="/")
    
    board_visual = get_board_state(match.board_state or "")
    return templates.TemplateResponse("tournament/game.html", {
        "request": request, "match": match, "board_visual": board_visual
    })

@router.post("/move/{match_id}")
def submit_move(match_id: int, move_data: MoveRequest, db: Session = Depends(database.get_db)):
    match = db.query(models.TournamentMatch).filter(models.TournamentMatch.id == match_id).first()
    if not match: return {"success": False, "message": "Match not found"}

    # --- 1. HUMAN MOVE ---
    engine = QuantumEngine()
    current_history = match.board_state if match.board_state else ""
    engine.load_game(current_history)

    if engine.apply_move(move_data.move_str):
        # Update DB for Human Move
        if current_history:
            new_history = f"{current_history},{move_data.move_str}"
        else:
            new_history = move_data.move_str
        
        match.board_state = new_history
        db.commit()
        
        # --- 2. CHECK FOR AI TURN ---
        # If Player 2 is CPU_AI, it plays immediately after
        if match.player2.username == "CPU_AI":
            # Initialize AI
            bot = QuantumAI()
            
            # The engine state is already updated with human move
            # We ask the AI for a list of candidates
            candidates = bot.calculate_move(engine)
            
            ai_move_made = False
            for cand in candidates:
                # Try the move on the real engine
                # Note: We need to reload engine state because apply_move mutates it
                # and if it fails, the state might be weird. 
                # Ideally, we create a fresh engine for every attempt.
                test_engine = QuantumEngine()
                test_engine.load_game(match.board_state) # Load current state (Human moved)
                
                if test_engine.apply_move(cand):
                    # Valid move found!
                    match.board_state = f"{match.board_state},{cand}"
                    db.commit()
                    ai_move_made = True
                    # Update the visual to return to frontend
                    engine = test_engine 
                    break
            
            if not ai_move_made:
                print("AI could not find a valid move (Stalemate or bug?)")

        return {"success": True, "new_board": engine.get_ascii_visual()}
    else:
        return {"success": False, "message": f"Illegal Quantum Move: {move_data.move_str}"}
