"""Source health monitoring and metrics tracking"""
from datetime import datetime, timezone, timedelta
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class SourceHealthMonitor:
    """Monitor crawler source health and performance"""
    
    def __init__(self, db):
        self.db = db
    
    async def record_crawl_attempt(
        self,
        source_name: str,
        status: str,
        facilities_found: int = 0,
        facilities_inserted: int = 0,
        error: str = None
    ):
        """Record a crawl attempt for health tracking"""
        health_entry = {
            "source_name": source_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": status,  # 'success', 'error', 'empty'
            "facilities_found": facilities_found,
            "facilities_inserted": facilities_inserted,
            "error": error
        }
        
        await self.db.source_health.insert_one(health_entry)
    
    async def get_source_health(self, source_name: str = None, days: int = 7) -> List[Dict]:
        """Get health metrics for sources"""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        query = {"timestamp": {"$gte": cutoff_date.isoformat()}}
        if source_name:
            query["source_name"] = source_name
        
        health_records = await self.db.source_health.find(
            query,
            {"_id": 0}
        ).sort("timestamp", -1).limit(100).to_list(100)
        
        return health_records
    
    async def get_source_statistics(self, days: int = 7) -> List[Dict]:
        """Get aggregated statistics per source"""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        pipeline = [
            {
                "$match": {
                    "timestamp": {"$gte": cutoff_date.isoformat()}
                }
            },
            {
                "$group": {
                    "_id": "$source_name",
                    "total_attempts": {"$sum": 1},
                    "successful_crawls": {
                        "$sum": {"$cond": [{"$eq": ["$status", "success"]}, 1, 0]}
                    },
                    "failed_crawls": {
                        "$sum": {"$cond": [{"$eq": ["$status", "error"]}, 1, 0]}
                    },
                    "empty_results": {
                        "$sum": {"$cond": [{"$eq": ["$status", "empty"]}, 1, 0]}
                    },
                    "total_facilities_found": {"$sum": "$facilities_found"},
                    "total_facilities_inserted": {"$sum": "$facilities_inserted"},
                    "last_crawl": {"$max": "$timestamp"}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "source_name": "$_id",
                    "total_attempts": 1,
                    "successful_crawls": 1,
                    "failed_crawls": 1,
                    "empty_results": 1,
                    "total_facilities_found": 1,
                    "total_facilities_inserted": 1,
                    "last_crawl": 1,
                    "success_rate": {
                        "$multiply": [
                            {"$divide": ["$successful_crawls", "$total_attempts"]},
                            100
                        ]
                    }
                }
            },
            {"$sort": {"total_facilities_inserted": -1}}
        ]
        
        stats = await self.db.source_health.aggregate(pipeline).to_list(100)
        return stats
    
    async def get_overall_health(self) -> Dict:
        """Get overall system health metrics"""
        # Last 24 hours
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        
        recent_attempts = await self.db.source_health.count_documents({
            "timestamp": {"$gte": cutoff.isoformat()}
        })
        
        successful_attempts = await self.db.source_health.count_documents({
            "timestamp": {"$gte": cutoff.isoformat()},
            "status": "success"
        })
        
        failed_attempts = await self.db.source_health.count_documents({
            "timestamp": {"$gte": cutoff.isoformat()},
            "status": "error"
        })
        
        # Get total facilities discovered in last 24 hours
        pipeline = [
            {"$match": {"timestamp": {"$gte": cutoff.isoformat()}}},
            {"$group": {
                "_id": None,
                "total_found": {"$sum": "$facilities_found"},
                "total_inserted": {"$sum": "$facilities_inserted"}
            }}
        ]
        
        aggregation = await self.db.source_health.aggregate(pipeline).to_list(1)
        totals = aggregation[0] if aggregation else {"total_found": 0, "total_inserted": 0}
        
        return {
            "period": "last_24_hours",
            "total_attempts": recent_attempts,
            "successful_attempts": successful_attempts,
            "failed_attempts": failed_attempts,
            "success_rate": (successful_attempts / recent_attempts * 100) if recent_attempts > 0 else 0,
            "facilities_discovered": totals["total_found"],
            "facilities_inserted": totals["total_inserted"]
        }
