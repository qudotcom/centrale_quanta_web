from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt

from app.core.database import engine, Base
from app.core import security # Ensure this import exists

# --- IMPORT ROUTERS ---
from app.modules.auth import router as auth_router
from app.modules.tournament import router as tournament_router
from app.modules.club import router as club_router

# --- IMPORT MODELS ---
from app.modules.auth import models as auth_models
from app.modules.tournament import models as tournament_models
from app.modules.club import models as club_models

# --- CREATE TABLES ---
Base.metadata.create_all(bind=engine)

# --- APP CONFIGURATION ---
app = FastAPI(title="Centrale Quanta Platform")

# --- CUSTOM MIDDLEWARE: INJECT USER INTO TEMPLATES ---
# This allows us to access {{ request.state.user }} in HTML
class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request.state.user = None
        token = request.cookies.get("access_token")
        
        if token:
            try:
                # The token comes as "Bearer <token>", we need to split it
                scheme, _, param = token.partition(" ")
                if scheme.lower() == "bearer":
                    # Decode token using the Secret Key from security module
                    payload = jwt.decode(param, security.SECRET_KEY, algorithms=[security.ALGORITHM])
                    username = payload.get("sub")
                    if username:
                        request.state.user = {"username": username}
            except Exception:
                # If token is invalid/expired, just ignore it (user is logged out)
                pass
                
        response = await call_next(request)
        return response

app.add_middleware(AuthMiddleware)

# --- MOUNT STATIC FILES ---
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# --- INCLUDE ROUTERS ---
app.include_router(auth_router.router, prefix="/auth", tags=["Authentication"])
app.include_router(tournament_router.router, prefix="/tournament", tags=["Quantum Tournament"])
app.include_router(club_router.router, tags=["Club Info"])

# --- ROOT ENDPOINT ---
@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("club/index.html", {"request": request})
