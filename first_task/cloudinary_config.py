import cloudinary
import cloudinary.uploader
from config import settings

cloudinary.config(
  cloud_name=settings.CLOUDINARY_NAME,
  api_key=settings.CLOUDINARY_API_KEY,
  api_secret=settings.CLOUDINARY_API_SECRET
)

def upload_avatar(file):
    result = cloudinary.uploader.upload(file.file, folder="avatars")
    return result["secure_url"]
