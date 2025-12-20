from fastapi import APIRouter, Depends, Request, Form, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.core import database, security
from app.modules.auth import models, schemas

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# --- VIEWS (HTML) ---
@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})

@router.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse("auth/register.html", {"request": request})

# --- ACTIONS (POST) ---

@router.post("/register")
async def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(database.get_db)
):
    # 1. Validate Input (Pydantic)
    try:
        user_data = schemas.UserCreate(username=username, email=email, password=password)
    except ValueError as e:
        return templates.TemplateResponse("auth/register.html", {"request": request, "error": "Invalid Data format."})

    # 2. Check Exists (SQLAlchemy prevents SQL Injection)
    existing_user = db.query(models.User).filter(
        (models.User.username == user_data.username) | (models.User.email == user_data.email)
    ).first()
    
    if existing_user:
        return templates.TemplateResponse("auth/register.html", {"request": request, "error": "Username or Email already taken."})

    # 3. Hash Password & Save
    hashed_pwd = security.get_password_hash(user_data.password)
    new_user = models.User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_pwd
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)

@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(database.get_db)
):
    # 1. Find User
    user = db.query(models.User).filter(models.User.username == username).first()
    
    # 2. Verify Password (Secure Compare)
    if not user or not security.verify_password(password, user.hashed_password):
        return templates.TemplateResponse("auth/login.html", {"request": request, "error": "Invalid Credentials"})

    # 3. Create Session (Server-Side Signed Cookie)
    request.session['user_id'] = user.id
    request.session['username'] = user.username
    
    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
