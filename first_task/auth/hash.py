from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

from fastapi import APIRouter, HTTPException, Depends
from redis_client import redis_client
from models import User  
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from schemas import Token
from auth import authenticate_user, create_access_token
from dependencies import get_db  

router = APIRouter(prefix="/auth")

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    
    await redis_client.setex(
        f"user:{user.id}", 
        3600,             
        user.json()        
    )

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}
