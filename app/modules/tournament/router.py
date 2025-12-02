from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.core import database
from app.modules.tournament import logic, models

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/bracket")
def view_bracket(request: Request, db: Session = Depends(database.get_db)):
    # Fetch all matches
    matches = db.query(models.TournamentMatch).all()
    return templates.TemplateResponse("tournament/bracket.html", {
        "request": request, 
        "matches": matches
    })

@router.post("/generate")
def start_tournament(db: Session = Depends(database.get_db)):
    result = logic.generate_single_elimination(db)
    if "error" in result:
        # In a real app, you'd flash a message. 
        # Here we just redirect back to bracket.
        print(f"Error: {result['error']}") 
    return RedirectResponse(url="/tournament/bracket", status_code=302)

@router.get("/play/{match_id}")
def play_match(match_id: int, request: Request, db: Session = Depends(database.get_db)):
    match = db.query(models.TournamentMatch).filter(models.TournamentMatch.id == match_id).first()
    if not match:
        return RedirectResponse(url="/tournament/bracket")
        
    return templates.TemplateResponse("tournament/game.html", {
        "request": request, 
        "match": match
    })
