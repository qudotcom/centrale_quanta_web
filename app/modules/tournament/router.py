from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core import database
from app.modules.tournament import logic, models
# Import the physics engine we created
from app.modules.tournament.engine import QuantumEngine, get_board_state

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# --- DATA MODELS ---
class MoveRequest(BaseModel):
    move_str: str

# --- ROUTES ---

@router.get("/bracket")
def view_bracket(request: Request, db: Session = Depends(database.get_db)):
    """
    Displays the visual tournament tree.
    """
    matches = db.query(models.TournamentMatch).all()
    return templates.TemplateResponse("tournament/bracket.html", {
        "request": request, 
        "matches": matches
    })

@router.post("/generate")
def start_tournament(db: Session = Depends(database.get_db)):
    """
    Admin action to wipe the database and start a random bracket.
    """
    result = logic.generate_single_elimination(db)
    
    if "error" in result:
        # In a production app, use Flash messages here.
        print(f"Tournament Error: {result['error']}")
        
    return RedirectResponse(url="/tournament/bracket", status_code=302)

@router.get("/play/{match_id}")
def play_match(match_id: int, request: Request, db: Session = Depends(database.get_db)):
    """
    The Game Cockpit. Loads the match and the current Quantum Board state.
    """
    match = db.query(models.TournamentMatch).filter(models.TournamentMatch.id == match_id).first()
    
    if not match:
        # If match doesn't exist, go back to bracket
        return RedirectResponse(url="/tournament/bracket")
        
    # 1. Get the current history string (e.g., "e2e4,e7e5")
    current_history = match.board_state if match.board_state else ""
    
    # 2. Replay history to get the ASCII visual
    board_visual = get_board_state(current_history)

    return templates.TemplateResponse("tournament/game.html", {
        "request": request, 
        "match": match,
        "board_visual": board_visual  # Validates the {{ board_visual }} in Jinja
    })

@router.post("/move/{match_id}")
def submit_move(match_id: int, move_data: MoveRequest, db: Session = Depends(database.get_db)):
    """
    Handles a move submission from the Javascript console.
    1. Replays old moves.
    2. Tries the new move.
    3. Saves if valid.
    """
    match = db.query(models.TournamentMatch).filter(models.TournamentMatch.id == match_id).first()
    if not match:
        return {"success": False, "message": "Match not found"}
    
    # 1. Initialize Engine & Replay History
    engine = QuantumEngine()
    current_history = match.board_state if match.board_state else ""
    engine.load_game(current_history)
    
    # 2. Attempt the new move
    if engine.apply_move(move_data.move_str):
        # 3. Update Database (Append new move to history)
        if current_history:
            new_history = f"{current_history},{move_data.move_str}"
        else:
            new_history = move_data.move_str
            
        match.board_state = new_history
        db.commit()
        
        # 4. Return success and the new board visual
        return {
            "success": True, 
            "new_board": engine.get_ascii_visual()
        }
    else:
        return {
            "success": False, 
            "message": f"Illegal Quantum Move: {move_data.move_str}"
        }
