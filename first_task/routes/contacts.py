from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List
from datetime import datetime, timedelta
from bson import ObjectId
from bson.errors import InvalidId

from db.mongo import contacts_collection
from models.contact import Contact, ContactUpdate
from utils.contact_helper import contact_helper
from auth.dependencies import get_current_user

router = APIRouter(prefix="/contacts", tags=["contacts"])



@router.post("/", response_model=Contact, status_code=201)
async def create_contact(contact: Contact, user=Depends(get_current_user)):
    contact_data = contact.dict()
    contact_data["birthday"] = datetime.combine(contact_data["birthday"], datetime.min.time())
    contact_data["owner_id"] = user["id"]

    if await contacts_collection.find_one({"email": contact_data["email"], "owner_id": user["id"]}):
        raise HTTPException(status_code=400, detail="Email вже використовується")
    if await contacts_collection.find_one({"phone": contact_data["phone"], "owner_id": user["id"]}):
        raise HTTPException(status_code=400, detail="Телефон вже використовується")

    result = await contacts_collection.insert_one(contact_data)
    new_contact = await contacts_collection.find_one({"_id": result.inserted_id})
    return contact_helper(new_contact)

@router.get("/", response_model=List[Contact])
async def list_contacts(search: Optional[str] = None, user=Depends(get_current_user)):
    query = {"owner_id": user["id"]}
    if search:
        query["$or"] = [
            {"first_name": {"$regex": search, "$options": "i"}},
            {"last_name": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}},
        ]
    contacts = []
    cursor = contacts_collection.find(query)
    async for document in cursor:
        contacts.append(contact_helper(document))
    return contacts

@router.get("/{contact_id}", response_model=Contact)
async def get_contact(contact_id: str, user=Depends(get_current_user)):
    try:
        oid = ObjectId(contact_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Невірний ідентифікатор контакту")

    contact = await contacts_collection.find_one({"_id": oid, "owner_id": user["id"]})
    if contact:
        return contact_helper(contact)
    raise HTTPException(status_code=404, detail="Контакт не знайдено")

@router.put("/{contact_id}", response_model=Contact)
async def update_contact(contact_id: str, contact_update: ContactUpdate, user=Depends(get_current_user)):
    try:
        oid = ObjectId(contact_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Невірний ідентифікатор контакту")

    contact_data = contact_update.dict()
    contact_data["birthday"] = datetime.combine(contact_data["birthday"], datetime.min.time())

    existing_email = await contacts_collection.find_one({"email": contact_data["email"], "_id": {"$ne": oid}, "owner_id": user["id"]})
    if existing_email:
        raise HTTPException(status_code=400, detail="Email вже використовується")

    existing_phone = await contacts_collection.find_one({"phone": contact_data["phone"], "_id": {"$ne": oid}, "owner_id": user["id"]})
    if existing_phone:
        raise HTTPException(status_code=400, detail="Телефон вже використовується")

    result = await contacts_collection.update_one({"_id": oid, "owner_id": user["id"]}, {"$set": contact_data})
    if result.modified_count == 1:
        updated_contact = await contacts_collection.find_one({"_id": oid})
        return contact_helper(updated_contact)
    raise HTTPException(status_code=404, detail="Контакт не знайдено")

@router.delete("/{contact_id}", status_code=204)
async def delete_contact(contact_id: str, user=Depends(get_current_user)):
    try:
        oid = ObjectId(contact_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Невірний ідентифікатор контакту")

    result = await contacts_collection.delete_one({"_id": oid, "owner_id": user["id"]})
    if result.deleted_count == 1:
        return
    raise HTTPException(status_code=404, detail="Контакт не знайдено")

@router.get("/upcoming-birthdays/", response_model=List[Contact])
async def upcoming_birthdays(user=Depends(get_current_user)):
    today = datetime.utcnow()
    in_seven_days = today + timedelta(days=7)

    pipeline = [
        {"$match": {"owner_id": user["id"]}},
        {
            "$addFields": {
                "birthMonth": {"$month": "$birthday"},
                "birthDay": {"$dayOfMonth": "$birthday"},
            }
        },
        {
            "$match": {
                "$expr": {
                    "$and": [
                        {
                            "$gte": [
                                {"$dateFromParts": {"year": today.year, "month": "$birthMonth", "day": "$birthDay"}},
                                today,
                            ]
                        },
                        {
                            "$lte": [
                                {"$dateFromParts": {"year": today.year, "month": "$birthMonth", "day": "$birthDay"}},
                                in_seven_days,
                            ]
                        },
                    ]
                }
            }
        },
    ]

    contacts = []
    async for doc in contacts_collection.aggregate(pipeline):
        contacts.append(contact_helper(doc))
    return contacts
