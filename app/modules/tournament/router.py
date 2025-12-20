from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pydantic import BaseModel
import time
import json
import random

from app.core import database
from app.modules.tournament import logic, models
from app.modules.auth.models import User 
from app.modules.tournament.engine import QuantumState, get_board_state
from app.modules.tournament.ai import QuantumAI

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

class MoveRequest(BaseModel):
    move_str: str

# --- HELPERS ---
def advance_winner(match, db):
    """Promotes the winner to the next bracket round."""
    if match.next_match_id and match.winner_id:
        next_match = db.query(models.TournamentMatch).filter(models.TournamentMatch.id == match.next_match_id).first()
        if next_match:
            if match.next_match_slot == 1:
                next_match.player1_id = match.winner_id
            elif match.next_match_slot == 2:
                next_match.player2_id = match.winner_id
            
            # If both slots filled, activate match
            if next_match.player1_id and next_match.player2_id:
                next_match.is_active = True
            
            db.commit()

def update_clocks(match):
    now = time.time()
    elapsed = now - (match.last_move_timestamp or now)
    p1 = match.p1_time_left or 600.0
    p2 = match.p2_time_left or 600.0
    
    if match.current_turn == "white":
        match.p1_time_left = max(0.0, p1 - elapsed)
        if match.p1_time_left == 0: return "black"
    else:
        match.p2_time_left = max(0.0, p2 - elapsed)
        if match.p2_time_left == 0: return "white"
    match.last_move_timestamp = now
    return None

def execute_ai_turn(match, db):
    bot = QuantumAI()
    engine = QuantumState()
    engine.load_game(match.board_state or "")
    ai_color = 'black' if match.player2.username == "CPU_AI" else 'white'
    diff = match.ai_difficulty or "normal"
    
    candidates = bot.calculate_move(engine, ai_color, diff)
    
    for cand in candidates:
        test = QuantumState()
        test.load_game(match.board_state or "")
        if test.apply_move(cand):
            match.board_state = f"{match.board_state},{cand}" if match.board_state else cand
            match.current_turn = "white" if match.current_turn == "black" else "black"
            match.last_move_timestamp = time.time()
            
            status = test.check_game_over()
            if status['game_over']:
                match.is_active = False
                match.winner_id = match.player1_id if status['winner'] == 'white' else match.player2_id
                advance_winner(match, db) # PROMOTE AI/PLAYER
            
            db.commit()
            db.refresh(match)
            return True
    return False

# --- ROUTES ---

@router.post("/practice")
async def start_practice_match(request: Request, db: Session = Depends(database.get_db)):
    form = await request.form()
    diff = form.get("difficulty", "normal")
    cpu_user = db.query(User).filter(User.username == "CPU_AI").first()
    if not cpu_user:
        cpu_user = User(username="CPU_AI", email="ai@q.com", hashed_password="x")
        db.add(cpu_user); db.commit()

    human = None
    if hasattr(request.state, 'user') and request.state.user:
        human = db.query(User).filter(User.username == request.state.user['username']).first()
    if not human:
        human = db.query(User).filter(User.username == "Guest").first() or User(username="Guest", email="g@g.com", hashed_password="x")
        db.add(human); db.commit()

    is_white = random.choice([True, False])
    p1, p2 = (human.id, cpu_user.id) if is_white else (cpu_user.id, human.id)

    match = models.TournamentMatch(
        tournament_id="PRACTICE", round_number=0, player1_id=p1, player2_id=p2, 
        board_state="", is_active=True, current_turn="white",
        p1_time_left=600.0, p2_time_left=600.0, last_move_timestamp=time.time(),
        ai_difficulty=diff
    )
    db.add(match); db.commit(); db.refresh(match)

    if not is_white: execute_ai_turn(match, db)
    return RedirectResponse(url=f"/tournament/play/{match.id}", status_code=302)

@router.get("/play/{match_id}")
def play_match(match_id: int, request: Request, db: Session = Depends(database.get_db)):
    match = db.query(models.TournamentMatch).filter(models.TournamentMatch.id == match_id).first()
    if not match: return RedirectResponse(url="/")
    
    update_clocks(match)
    state = get_board_state(match.board_state or "")
    user_color = 'white'
    cur = request.state.user['username'] if (hasattr(request, 'state') and request.state.user) else "Guest"
    if match.player2.username == cur or match.player1.username == "CPU_AI": user_color = 'black'
    
    return templates.TemplateResponse("tournament/game.html", {
        "request": request, "match": match, 
        "board_data": json.dumps(state['board_data'], default=str),
        "user_color": user_color, "current_turn": match.current_turn,
        "p1_time": match.p1_time_left, "p2_time": match.p2_time_left
    })

@router.post("/move/{match_id}")
def submit_move(match_id: int, move_data: MoveRequest, request: Request, db: Session = Depends(database.get_db)):
    match = db.query(models.TournamentMatch).filter(models.TournamentMatch.id == match_id).first()
    if not match.is_active: return {"success": False, "message": "Game Over"}

    winner = update_clocks(match)
    if winner: 
        match.is_active = False; match.winner_id = match.player1_id if winner=='white' else match.player2_id
        advance_winner(match, db)
        db.commit()
        return {"success": False, "message": "Time Out", "game_over": True, "winner": winner}

    req_user = request.state.user['username'] if (hasattr(request, 'state') and request.state.user) else "Guest"
    is_p1 = (match.player1.username == req_user)
    is_p2 = (match.player2.username == req_user)
    
    if match.current_turn == "white" and not is_p1: return {"success": False, "message": "Not your turn"}
    if match.current_turn == "black" and not is_p2: return {"success": False, "message": "Not your turn"}

    engine = QuantumState()
    engine.load_game(match.board_state or "")

    if engine.apply_move(move_data.move_str):
        match.board_state = f"{match.board_state},{move_data.move_str}" if match.board_state else move_data.move_str
        match.current_turn = "black" if match.current_turn == "white" else "white"
        db.commit()
        
        status = engine.check_game_over()
        if status['game_over']:
            match.is_active = False
            match.winner_id = match.player1_id if status['winner'] == 'white' else match.player2_id
            advance_winner(match, db)
            db.commit()
            return {"success": True, "board_data": engine.get_frontend_board(), "game_over": True, "winner": status['winner']}

        ai_moved = False
        if "CPU_AI" in [match.player1.username, match.player2.username]:
            ai_moved = execute_ai_turn(match, db)
            db.refresh(match)
            engine.load_game(match.board_state)
            status = engine.check_game_over()

        return {
            "success": True, 
            "board_data": engine.get_frontend_board(), 
            "game_over": status['game_over'], 
            "winner": status.get('winner'),
            "ai_moved": ai_moved,
            "p1_time": match.p1_time_left,
            "p2_time": match.p2_time_left,
            "current_turn": match.current_turn
        }
    
    return {"success": False, "message": "Illegal Move"}

# Helper routes
@router.post("/seed")
def seed_participants(db: Session = Depends(database.get_db)): return RedirectResponse(url="/tournament/bracket", status_code=302)
@router.get("/bracket")
def view_bracket(request: Request, db: Session = Depends(database.get_db)):
    # Show active and completed matches, sorted by time
    matches = db.query(models.TournamentMatch).order_by(models.TournamentMatch.created_at.desc()).all()
    return templates.TemplateResponse("tournament/bracket.html", {"request": request, "matches": matches})
@router.post("/generate")
def start_tournament(db: Session = Depends(database.get_db)):
    logic.generate_single_elimination(db)
    return RedirectResponse(url="/tournament/bracket", status_code=302)
