import re
import unicodedata
import urllib.parse
from backend.models import EntityType

def normalize_input(text: str) -> str:
    """
    Applies rigorous normalization to input text to defeat consistency attacks.
    1. Unicode Normalization (NFKC) -> fixes homoglyphs (e.g. 𝟷 -> 1)
    2. URL Decoding -> fixes %20, %3A etc.
    3. Strip Zero-width characters
    """
    if not text:
        return ""
    
    # 1. URL Decode first (in case obfuscation uses % encoding)
    try:
        text = urllib.parse.unquote(text)
    except:
        pass

    # 2. Unicode Normalization (NFKC is best for compatibility)
    text = unicodedata.normalize('NFKC', text)
    
    # 3. Remove zero-width characters (ZWNJ, ZWJ, etc.)
    # \u200B-\u200D (Zero width space, Joiner, Non-Joiner)
    # \uFEFF (Zero width no-break space)
    text = re.sub(r'[\u200B-\u200D\uFEFF]', '', text)
    
    return text.strip()

def detect_type(value: str) -> EntityType:
    """
    Legacy single-type detection. 
    Use extract_entities for multi-vector analysis.
    """
    # Quick normalization for detection
    val = normalize_input(value)
    
    if re.match(r"^[a-zA-Z0-9.\-_]+@[a-zA-Z]+$", val):
        return EntityType.UPI
    
    # Simple regex for phone (relaxed)
    # starts with optional +, then 10-15 digits allowed with spaces/dashes
    if re.match(r"^\+?[0-9\-\s]{10,16}$", val):
        return EntityType.PHONE
        
    if re.match(r"^https?://", val) or re.match(r"^www\.", val):
        return EntityType.URL
        
    return EntityType.MESSAGE_TEXT

def extract_entities(text: str) -> dict:
    """
    Extracts all potential entities from a block of text.
    Returns: {
        'phones': [],
        'upis': [],
        'urls': []
    }
    """
    normalized = normalize_input(text)
    entities = {
        "phones": [],
        "upis": [],
        "urls": []
    }
    
    # 1. Extract URLs
    # Pattern looks for http/https or www.
    url_pattern = r'(https?://[^\s]+|www\.[^\s]+)'
    entities['urls'] = re.findall(url_pattern, normalized)
    
    # 2. Extract UPIs
    # Pattern: something@bankname
    # Exclude email-like patterns if needed, but UPIs are subset of emails often
    upi_pattern = r'[a-zA-Z0-9.\-_]+@[a-zA-Z]{2,}'
    # Filter out potential emails if necessary, but for now grab all handle@bank
    found_upis = re.findall(upi_pattern, normalized)
    entities['upis'] = [u for u in found_upis if not u.startswith("http")] # simple filter
    
    # 3. Extract Phones
    # Look for groups of digits.
    # +91 99999 99999 or 9999999999
    # E.164-ish regex
    phone_pattern = r'(?:\+|00)?(?:[0-9][\-\s]*){10,15}'
    # This is a bit broad, might catch random numbers. 
    # Let's clean matches.
    raw_phones = re.findall(phone_pattern, normalized)
    valid_phones = []
    for p in raw_phones:
        cleaned = re.sub(r'[\-\s]', '', p)
        if len(cleaned) >= 10:
            valid_phones.append(cleaned)
    entities['phones'] = list(set(valid_phones)) # Dedup
    
    return entities

def validate_entity_type(value: str, expected_type: EntityType) -> bool:
    detected = detect_type(value)
    if expected_type == EntityType.MESSAGE_TEXT:
        return True
    if expected_type == EntityType.OTHER:
        return True
    return detected == expected_type
