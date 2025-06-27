from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from models.user import User, UserResponse, Token, UserCreate
from auth.hash import get_password_hash, verify_password
from auth.jwt import create_access_token, create_refresh_token
from db.mongo import users_collection
from sqlalchemy.orm import Session
from db import get_db
from auth import jwt 
from utils.email import send_verification_email, get_user_by_email
from config import settings
from datetime import datetime, timedelta

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(user: User):
    existing = await users_collection.find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=409, detail="Email вже існує")
    hashed = get_password_hash(user.password)
    result = await users_collection.insert_one({"email": user.email, "password": hashed})
    return {"id": str(result.inserted_id), "email": user.email}

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await users_collection.find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Невірний email або пароль")

    access = create_access_token(data={"sub": user["email"]})
    refresh = create_refresh_token(data={"sub": user["email"]})
    return {"access_token": access, "refresh_token": refresh}

@router.post("/register")
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Create user in DB (example, adjust as needed)
    user = User(email=user_data.email, password=get_password_hash(user_data.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    token = jwt.encode(
        {"sub": user.email, "exp": datetime.utcnow() + timedelta(hours=2)},
        settings.SECRET_KEY,
        algorithm="HS256"
    )
    await send_verification_email(user.email, token)
    return {"msg": "Check your email to verify your account"}

@router.get("/verify/{token}")
async def verify_email(token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        email = payload.get("sub")
        user = get_user_by_email(db, email)
        if user:
            user.is_verified = True
            db.commit()
            return {"msg": "Email verified"}
    except jwt.ExpiredSignatureError:
        raise HTTPException(400, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(400, detail="Invalid token")