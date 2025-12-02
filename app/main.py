from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.core.database import engine, Base

# --- IMPORT ROUTERS ---
from app.modules.auth import router as auth_router
# Note: Ensure you have at least an empty router in club if you haven't built it yet
# from app.modules.club import router as club_router 
from app.modules.tournament import router as tournament_router

# --- IMPORT MODELS ---
# We import models here to ensure SQLAlchemy creates the tables on startup
from app.modules.auth import models as auth_models
from app.modules.tournament import models as tournament_models
# from app.modules.club import models as club_models

# --- CREATE TABLES ---
Base.metadata.create_all(bind=engine)

# --- APP CONFIGURATION ---
app = FastAPI(
    title="Centrale Quanta Platform",
    description="The Quantum Chess & Computing Club Interface",
    version="1.0.0"
)

# --- MOUNT STATIC FILES ---
# CSS, JS, Images served from /static
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# --- INCLUDE ROUTERS ---
app.include_router(auth_router.router, prefix="/auth", tags=["Authentication"])
app.include_router(tournament_router.router, prefix="/tournament", tags=["Quantum Tournament"])

# Uncomment when Club module is ready
# app.include_router(club_router.router, tags=["Club Info"])

# --- ROOT ENDPOINT ---
@app.get("/")
def root():
    # In a real app, this would render the templates/club/index.html
    # using Jinja2, but for now we return a JSON status or redirect.
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/tournament/bracket") 

# --- CRITICAL NOTE FOR THE USER ---
# The game.html uses a POST request to send moves. 
# You must ensure your app/modules/tournament/router.py has a route like:
# @router.post("/move/{match_id}")
