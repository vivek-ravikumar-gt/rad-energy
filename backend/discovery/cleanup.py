"""Database cleanup utilities"""
import logging
from motor.motor_asyncio import AsyncIOMotorDatabase
from .validation import FacilityValidator

logger = logging.getLogger(__name__)

class DatabaseCleanup:
    """Utilities for cleaning invalid facilities from database"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def remove_generic_entries(self) -> dict:
        """Remove generic and invalid company entries from database
        
        Returns:
            Dict with cleanup statistics
        """
        logger.info("Starting database cleanup...")
        
        # Get all facilities
        facilities = await self.db.industrial_facilities.find(
            {},
            {"_id": 0, "id": 1, "company_name": 1}
        ).to_list(10000)
        
        removed_count = 0
        removed_names = []
        
        for facility in facilities:
            company_name = facility.get('company_name', '')
            
            # Check if generic
            if FacilityValidator.is_generic_entry(company_name):
                # Delete this entry
                result = await self.db.industrial_facilities.delete_one(
                    {"id": facility['id']}
                )
                
                if result.deleted_count > 0:
                    removed_count += 1
                    removed_names.append(company_name)
                    logger.info(f"Removed generic entry: {company_name}")
        
        logger.info(f"Cleanup complete: Removed {removed_count} entries")
        
        return {
            "removed_count": removed_count,
            "removed_names": removed_names[:50],  # First 50 for display
            "total_removed_names": len(removed_names)
        }
    
    async def remove_incomplete_entries(self) -> dict:
        """Remove entries missing required fields (company_name, city, or industry)
        
        Returns:
            Dict with cleanup statistics
        """
        logger.info("Removing incomplete entries...")
        
        # Find entries missing required fields
        query = {
            "$or": [
                {"company_name": {"$exists": False}},
                {"company_name": ""},
                {"company_name": None},
                {"city": {"$exists": False}},
                {"city": ""},
                {"city": None},
                {"industry_type": {"$exists": False}},
                {"industry_type": ""},
                {"industry_type": None}
            ]
        }
        
        # Count first
        count = await self.db.industrial_facilities.count_documents(query)
        
        # Delete
        result = await self.db.industrial_facilities.delete_many(query)
        
        logger.info(f"Removed {result.deleted_count} incomplete entries")
        
        return {
            "removed_count": result.deleted_count
        }
    
    async def get_cleanup_preview(self) -> dict:
        """Preview what would be removed without actually removing
        
        Returns:
            Dict with preview statistics
        """
        # Get all facilities
        facilities = await self.db.industrial_facilities.find(
            {},
            {"_id": 0, "id": 1, "company_name": 1, "city": 1, "industry_type": 1}
        ).to_list(10000)
        
        generic_count = 0
        incomplete_count = 0
        generic_examples = []
        incomplete_examples = []
        
        for facility in facilities:
            company_name = facility.get('company_name', '')
            city = facility.get('city', '')
            industry = facility.get('industry_type', '')
            
            # Check if incomplete
            if not company_name or not city or not industry:
                incomplete_count += 1
                if len(incomplete_examples) < 10:
                    incomplete_examples.append({
                        "name": company_name or "(missing)",
                        "city": city or "(missing)",
                        "industry": industry or "(missing)"
                    })
            
            # Check if generic
            if company_name and FacilityValidator.is_generic_entry(company_name):
                generic_count += 1
                if len(generic_examples) < 10:
                    generic_examples.append(company_name)
        
        return {
            "total_facilities": len(facilities),
            "generic_count": generic_count,
            "incomplete_count": incomplete_count,
            "would_remove": generic_count + incomplete_count,
            "generic_examples": generic_examples,
            "incomplete_examples": incomplete_examples
        }
