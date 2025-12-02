from fastapi import APIRouter, Depends, HTTPException, status, Request, Form, Response
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import timedelta

from app.core import database, security
from app.modules.auth import models

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# --- REGISTER ---
@router.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse("auth/register.html", {"request": request})

@router.post("/register")
def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(database.get_db)
):
    # Check if user exists
    user = db.query(models.User).filter(models.User.email == email).first()
    if user:
        return templates.TemplateResponse("auth/register.html", {
            "request": request, "error": "Email already registered"
        })
    
    # Create new user
    hashed_password = security.get_password_hash(password)
    new_user = models.User(
        email=email, 
        username=username, 
        hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Redirect to login page
    return RedirectResponse(url="/auth/login", status_code=302)

# --- LOGIN ---
@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})

@router.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(database.get_db)
):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not security.verify_password(password, user.hashed_password):
        return templates.TemplateResponse("auth/login.html", {
            "request": request, "error": "Invalid credentials"
        })
    
    # Create Token
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    # Set Cookie and Redirect
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(
        key="access_token", 
        value=f"Bearer {access_token}", 
        httponly=True  # Important for security
    )
    return response

@router.get("/logout")
def logout():
    response = RedirectResponse(url="/auth/login")
    response.delete_cookie("access_token")
    return response
