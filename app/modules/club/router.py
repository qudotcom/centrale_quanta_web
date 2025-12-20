from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.core import database
from app.modules.club import models

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# --- HELPER: SEED DATA IF EMPTY ---
def seed_club_data(db: Session):
    if db.query(models.BoardMember).count() == 0:
        # Create Dummy Board
        members = [
            models.BoardMember(name="Alice Quantum", role="President", bio="Obsessed with Entanglement."),
            models.BoardMember(name="Bob Bit", role="Vice President", bio="Master of Python and Potentials."),
            models.BoardMember(name="Charlie Cat", role="Treasurer", bio="Is he rich? Only when you observe him.")
        ]
        db.add_all(members)
        
        # Create Dummy Activities
        activities = [
            models.Activity(title="Qiskit Workshop 101", date="2025-10-15", description="Introduction to IBM's quantum SDK."),
            models.Activity(title="The Quantum Chess Tournament", date="2025-12-20", description="The ultimate showdown of superposition.")
        ]
        db.add_all(activities)
        db.commit()

@router.get("/about")
def about_page(request: Request, db: Session = Depends(database.get_db)):
    # 1. Seed data if empty (For your MVP convenience)
    seed_club_data(db)
    
    # 2. Fetch Data
    members = db.query(models.BoardMember).all()
    activities = db.query(models.Activity).all()
    
    return templates.TemplateResponse("club/board.html", {
        "request": request,
        "members": members,
        "activities": activities
    })
