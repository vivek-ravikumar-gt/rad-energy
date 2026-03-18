"""Main discovery pipeline orchestrator"""
import asyncio
from datetime import datetime, timezone
from typing import List, Dict
from motor.motor_asyncio import AsyncIOMotorDatabase
import uuid
import logging

from .demo_crawler import DemoCrawler, DEMO_SOURCES
from .real_crawler import RealCrawler, REAL_SOURCE_TEMPLATES
from .estimator import estimate_facility_metrics
from .deduplicator import is_duplicate

logger = logging.getLogger(__name__)

class DiscoveryPipeline:
    """Main pipeline for discovering and inserting facilities"""
    
    def __init__(self, db: AsyncIOMotorDatabase, mode: str = 'demo'):
        self.db = db
        self.mode = mode  # 'demo' or 'real'
        self.total_discovered = 0
        self.total_inserted = 0
        self.total_duplicates = 0
        self.logs = []
    
    async def run_discovery(self) -> Dict:
        """Run the complete discovery pipeline"""
        logger.info(f"Starting discovery pipeline in {self.mode} mode")
        start_time = datetime.now(timezone.utc)
        
        try:
            # Get all sources based on mode
            sources = await self._get_sources()
            
            # Crawl all sources
            all_facilities = []
            for source_config in sources:
                facilities = await self._crawl_source(source_config)
                all_facilities.extend(facilities)
                self.total_discovered += len(facilities)
            
            logger.info(f"Discovered {len(all_facilities)} facilities from {len(sources)} sources")
            
            # Process and insert facilities
            for facility_data in all_facilities:
                inserted = await self._process_facility(facility_data)
                if inserted:
                    self.total_inserted += 1
                else:
                    self.total_duplicates += 1
            
            # Create discovery log
            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds()
            
            log_entry = {
                "id": str(uuid.uuid4()),
                "mode": self.mode,
                "status": "success",
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": duration,
                "sources_crawled": len(sources),
                "facilities_discovered": self.total_discovered,
                "facilities_inserted": self.total_inserted,
                "duplicates_skipped": self.total_duplicates,
                "logs": self.logs
            }
            
            # Save discovery log to database
            await self.db.discovery_logs.insert_one(log_entry)
            
            logger.info(
                f"Discovery complete: {self.total_inserted} inserted, "
                f"{self.total_duplicates} duplicates skipped"
            )
            
            return {
                "status": "success",
                "facilities_discovered": self.total_discovered,
                "facilities_inserted": self.total_inserted,
                "duplicates_skipped": self.total_duplicates,
                "duration_seconds": duration
            }
        
        except Exception as e:
            logger.error(f"Discovery pipeline error: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "facilities_discovered": self.total_discovered,
                "facilities_inserted": self.total_inserted
            }
    
    async def _get_sources(self) -> List[Dict]:
        """Get crawler sources based on mode"""
        if self.mode == 'demo':
            return DEMO_SOURCES
        else:
            # Get enabled real sources from database
            sources = await self.db.discovery_sources.find({"enabled": True}).to_list(100)
            return sources if sources else REAL_SOURCE_TEMPLATES
    
    async def _crawl_source(self, source_config: Dict) -> List[Dict]:
        """Crawl a single source"""
        try:
            if self.mode == 'demo':
                crawler = DemoCrawler(
                    source_config['name'],
                    source_config['type'],
                    source_config.get('max_facilities', 10)
                )
            else:
                # Use production crawler for real sources
                from .production_crawler import ProductionCrawler
                crawler = ProductionCrawler(
                    source_config['name'],
                    source_config['type'],
                    source_config['url'],
                    source_config['selectors']
                )
            
            facilities = await crawler.crawl()
            
            self.logs.append({
                "source": source_config['name'],
                "status": "success",
                "facilities_found": len(facilities),
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
            return facilities
        
        except Exception as e:
            logger.error(f"Error crawling {source_config['name']}: {str(e)}")
            self.logs.append({
                "source": source_config['name'],
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            return []
    
    async def _process_facility(self, facility_data: Dict) -> bool:
        """Process and insert a single facility"""
        try:
            # Check for duplicates
            if await is_duplicate(
                self.db,
                facility_data['company_name'],
                facility_data['city']
            ):
                logger.debug(f"Duplicate facility: {facility_data['company_name']}")
                return False
            
            # Estimate metrics
            metrics = estimate_facility_metrics(
                facility_data['industry_type'],
                facility_data['industrial_cluster']
            )
            
            # Merge data
            facility = {
                "id": str(uuid.uuid4()),
                **facility_data,
                **metrics,
                "existing_renewable_adoption": False,
                "contact_email": None,
                "website": None,
                "date_added": datetime.now(timezone.utc).isoformat()
            }
            
            # Insert into database
            await self.db.industrial_facilities.insert_one(facility)
            logger.info(f"Inserted facility: {facility_data['company_name']}")
            
            return True
        
        except Exception as e:
            logger.error(f"Error processing facility {facility_data.get('company_name')}: {str(e)}")
            return False
