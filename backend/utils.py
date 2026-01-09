import re
from backend.models import EntityType

def detect_type(value: str) -> EntityType:
    if re.match(r"^[a-zA-Z0-9.\-_]+@[a-zA-Z]+$", value):
        return EntityType.UPI
    if re.match(r"^\+?[0-9\-\s]{10,}$", value):
        return EntityType.PHONE
    if re.match(r"^https?://", value) or re.match(r"^www\.", value):
        return EntityType.URL
    return EntityType.MESSAGE_TEXT

def validate_entity_type(value: str, expected_type: EntityType) -> bool:
    detected = detect_type(value)
    # Allow MESSAGE_TEXT to be loose, but others should generally match
    if expected_type == EntityType.MESSAGE_TEXT:
        return True
    if expected_type == EntityType.OTHER:
        return True
    return detected == expected_type
