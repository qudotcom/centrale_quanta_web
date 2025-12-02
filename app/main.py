from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.core.database import engine, Base

# Import models so tables are created
from app.modules.auth import models as auth_models
from app.modules.tournament import models as tournament_models 
# (Make sure tournament/models.py exists, even if empty, or comment out above line)

# Create Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Centrale Quanta Platform")

# Mount Static Files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
def read_root():
    return {"status": "System Operational", "club": "Centrale Quanta"}
