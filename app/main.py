from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.core.database import engine, Base

# --- 1. IMPORT ROUTERS ---
# These handle the URL logic for each section of your site
from app.modules.auth import router as auth_router
from app.modules.tournament import router as tournament_router
from app.modules.club import router as club_router

# --- 2. IMPORT MODELS ---
# We must import these so SQLAlchemy knows to create the tables (users, matches, board_members)
# when the app starts.
from app.modules.auth import models as auth_models
from app.modules.tournament import models as tournament_models
from app.modules.club import models as club_models

# --- 3. CREATE DATABASE TABLES ---
# This looks at all the imported models above and builds the SQLite file
Base.metadata.create_all(bind=engine)

# --- 4. APP CONFIGURATION ---
app = FastAPI(
    title="Centrale Quanta Platform",
    description="The Quantum Chess & Computing Club Interface",
    version="1.0.0"
)

# --- 5. MOUNT STATIC FILES ---
# This allows the HTML to find your CSS and JS at /static/...
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Setup Templates for the Root route
templates = Jinja2Templates(directory="app/templates")

# --- 6. INCLUDE ROUTERS ---
# Authentication (Login/Register)
app.include_router(auth_router.router, prefix="/auth", tags=["Authentication"])

# Tournament (Brackets/Game)
app.include_router(tournament_router.router, prefix="/tournament", tags=["Quantum Tournament"])

# Club (Board Members/Activities/About)
# We don't add a prefix like '/club' here if we want /about to be at the root level, 
# but usually it's cleaner to keep it modular. Let's keep it simple.
app.include_router(club_router.router, tags=["Club Info"]) 

# --- 7. ROOT ENDPOINT ---
@app.get("/")
def read_root(request: Request):
    """
    Renders the Landing Page (Green Fabric Theme).
    """
    # This points to app/templates/club/index.html
    return templates.TemplateResponse("club/index.html", {"request": request})
