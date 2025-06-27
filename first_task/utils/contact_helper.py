def contact_helper(contact) -> dict:
    return {
        "id": str(contact["_id"]),
        "first_name": contact["first_name"],
        "last_name": contact["last_name"],
        "email": contact["email"],
        "phone": contact["phone"],
        "birthday": contact["birthday"].date(),
        "additional_data": contact.get("additional_data"),
    }
