from fastapi import APIRouter, UploadFile, File, Depends
from models import contact 
from dependencies import get_current_user  
from utils import upload_avatar  
from db import mongo
router = APIRouter()

@router.post("/avatar")
async def update_avatar(file: UploadFile = File(...), user: contact.Contact = Depends(get_current_user)):
    url = await upload_avatar(file)
    user.avatar_url = url
    return {"avatar_url": url}
