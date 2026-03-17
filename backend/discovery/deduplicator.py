"""Deduplication logic to avoid inserting duplicate facilities"""
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional
import re

def normalize_company_name(name: str) -> str:
    """Normalize company name for comparison"""
    # Remove common suffixes
    name = re.sub(r'\b(Ltd|Limited|Pvt|Private|Inc|Corporation|Corp)\b\.?', '', name, flags=re.IGNORECASE)
    # Remove special characters and extra spaces
    name = re.sub(r'[^a-zA-Z0-9\s]', '', name)
    name = re.sub(r'\s+', ' ', name)
    return name.strip().lower()

async def check_duplicate(
    db: AsyncIOMotorDatabase,
    company_name: str,
    city: str
) -> Optional[dict]:
    """Check if facility already exists in database"""
    normalized_name = normalize_company_name(company_name)
    
    # Exact match check
    existing = await db.industrial_facilities.find_one({
        "company_name": company_name,
        "city": city
    }, {"_id": 0})
    
    if existing:
        return existing
    
    # Fuzzy match check - find similar names in same city
    all_facilities = await db.industrial_facilities.find(
        {"city": city},
        {"_id": 0, "company_name": 1, "id": 1}
    ).to_list(1000)
    
    for facility in all_facilities:
        if normalize_company_name(facility["company_name"]) == normalized_name:
            return await db.industrial_facilities.find_one(
                {"id": facility["id"]},
                {"_id": 0}
            )
    
    return None

async def is_duplicate(
    db: AsyncIOMotorDatabase,
    company_name: str,
    city: str
) -> bool:
    """Check if facility is a duplicate"""
    duplicate = await check_duplicate(db, company_name, city)
    return duplicate is not None
