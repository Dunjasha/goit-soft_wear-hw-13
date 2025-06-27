from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date

class Contact(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    birthday: date
    additional_data: Optional[str] = None

class ContactUpdate(Contact):
    pass
