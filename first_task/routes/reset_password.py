from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas import EmailSchema
from db import mongo
from models import get_user_by_email
from utils import generate_password_reset_token, send_reset_password_email, hash_password
from auth import jwt
from config import settings

router = APIRouter()

@router.post("/request-reset")
async def request_password_reset(data: EmailSchema, db: Session = Depends(get_db)):
    user = get_user_by_email(db, data.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    token = generate_password_reset_token(user.email)
    await send_reset_password_email(user.email, token)
    return {"msg": "Check your email for password reset instructions"}

@router.post("/reset-password/{token}")
async def reset_password(token: str, new_password: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        email = payload.get("sub")
    except jwt.PyJWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = hash_password(new_password)  
    db.commit()
    return {"msg": "Password reset successful"}
