from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware 

from app.core import database
from app.modules.auth import router as auth_router, models as auth_models
from app.modules.tournament import router as tournament_router, models as tourney_models

# Init DB Tables
auth_models.Base.metadata.create_all(bind=database.engine)
tourney_models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# Mount Static & Templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# --- 1. DEFINE AUTH MIDDLEWARE FIRST ---
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    username = request.session.get("username")
    if username:
        request.state.user = {"username": username}
    else:
        request.state.user = None
    
    response = await call_next(request)
    return response

# --- 2. ADD SESSION MIDDLEWARE LAST ---
app.add_middleware(SessionMiddleware, secret_key="SUPER_SECRET_QUANTUM_KEY_CHANGE_THIS")

# --- 3. ROUTERS ---
app.include_router(auth_router.router, prefix="/auth", tags=["auth"])
app.include_router(tournament_router.router, prefix="/tournament", tags=["tournament"])

# --- 4. ROUTES ---
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("club/index.html", {"request": request})

# THE MISSING LINK: This connects the URL to the HTML file
@app.get("/club_data")
def club_data(request: Request):
    return templates.TemplateResponse("club/board.html", {"request": request})
