from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_TLS=True,
    MAIL_SSL=False,
    USE_CREDENTIALS=True,
)

async def send_verification_email(email: str, token: str):
    message = MessageSchema(
        subject="Email Verification",
        recipients=[email],
        body=f"Click the link to verify: http://localhost:8000/api/auth/verify/{token}",
        subtype="html",
    )
    fm = FastMail(conf)
    await fm.send_message(message)
