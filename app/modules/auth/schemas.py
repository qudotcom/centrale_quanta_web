from pydantic import BaseModel, EmailStr, constr

# Base Schema
class UserBase(BaseModel):
    username: constr(min_length=3, max_length=50, strip_whitespace=True)
    email: EmailStr

# Schema for CREATING a user (Register)
class UserCreate(UserBase):
    # Enforce minimum password strength
    password: constr(min_length=6) 

# Schema for LOGGING IN
class UserLogin(BaseModel):
    username: str
    password: str
