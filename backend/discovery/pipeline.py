"""Main discovery pipeline orchestrator"""
import asyncio
from datetime import datetime, timezone
from typing import List, Dict
from motor.motor_asyncio import AsyncIOMotorDatabase
import uuid
import logging

from .demo_crawler import DemoCrawler, DEMO_SOURCES
from .production_crawler import ProductionCrawler
from .estimator import estimate_facility_metrics
from .deduplicator import is_duplicate
from .validation import FacilityValidator
from .geocoding import GeocodingService, get_fallback_coordinates
from .health_monitor import SourceHealthMonitor

logger = logging.getLogger(__name__)

class DiscoveryPipeline:
    """Main pipeline for discovering and inserting facilities"""
    
    def __init__(self, db: AsyncIOMotorDatabase, mode: str = 'demo'):
        self.db = db
        self.mode = mode  # 'demo' or 'real'
        self.total_discovered = 0
        self.total_inserted = 0
        self.total_duplicates = 0
        self.total_invalid = 0
        self.logs = []
        self.geocoder = GeocodingService()
        self.health_monitor = SourceHealthMonitor(db)
    
    async def run_discovery(self) -> Dict:
        """Run the complete discovery pipeline"""
        logger.info(f"Starting discovery pipeline in {self.mode} mode")
        start_time = datetime.now(timezone.utc)
        
        try:
            # Get all sources based on mode
            sources = await self._get_sources()
            
            if not sources:
                logger.warning("No sources available for discovery")
                return {
                    "status": "error",
                    "error": "No discovery sources configured",
                    "facilities_discovered": 0,
                    "facilities_inserted": 0
                }
            
            # Crawl all sources
            all_facilities = []
            for source_config in sources:
                facilities = await self._crawl_source(source_config)
                all_facilities.extend(facilities)
                self.total_discovered += len(facilities)
            
            logger.info(f"Discovered {len(all_facilities)} facilities from {len(sources)} sources")
            
            # Process and insert facilities
            for facility_data in all_facilities:
                result = await self._process_facility(facility_data)
                if result == 'inserted':
                    self.total_inserted += 1
                elif result == 'duplicate':
                    self.total_duplicates += 1
                elif result == 'invalid':
                    self.total_invalid += 1
            
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
                "invalid_rejected": self.total_invalid,
                "logs": self.logs
            }
            
            # Save discovery log to database
            await self.db.discovery_logs.insert_one(log_entry)
            
            logger.info(
                f"Discovery complete: {self.total_inserted} inserted, "
                f"{self.total_duplicates} duplicates, {self.total_invalid} invalid"
            )
            
            return {
                "status": "success",
                "facilities_discovered": self.total_discovered,
                "facilities_inserted": self.total_inserted,
                "duplicates_skipped": self.total_duplicates,
                "invalid_rejected": self.total_invalid,
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
        """Get crawler sources - ONLY real sources, demo mode disabled"""
        # Get enabled real sources from database ONLY
        sources = await self.db.discovery_sources.find({"enabled": True}, {"_id": 0}).to_list(100)
        if not sources:
            logger.warning("No enabled production sources found")
            return []
        return sources
    
    async def _crawl_source(self, source_config: Dict) -> List[Dict]:
        """Crawl a single source with health monitoring - production only"""
        source_name = source_config['name']
        
        try:
            # Always use production crawler (demo mode disabled)
            crawler = ProductionCrawler(
                source_config['name'],
                source_config['type'],
                source_config['url'],
                source_config['selectors']
            )
            
            facilities = await crawler.crawl()
            
            # Record health
            status = 'success' if facilities else 'empty'
            await self.health_monitor.record_crawl_attempt(
                source_name,
                status,
                facilities_found=len(facilities)
            )
            
            self.logs.append({
                "source": source_config['name'],
                "status": status,
                "facilities_found": len(facilities),
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
            return facilities
        
        except Exception as e:
            logger.error(f"Error crawling {source_config['name']}: {str(e)}")
            
            # Record health
            await self.health_monitor.record_crawl_attempt(
                source_name,
                'error',
                error=str(e)
            )
            
            self.logs.append({
                "source": source_config['name'],
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            return []
    
    async def _process_facility(self, facility_data: Dict) -> str:
        """Process and insert a single facility with validation
        
        Returns:
            'inserted', 'duplicate', or 'invalid'
        """
        try:
            # Validate facility data
            is_valid, error_msg = FacilityValidator.validate_facility(facility_data)
            if not is_valid:
                logger.debug(f"Invalid facility: {facility_data.get('company_name')} - {error_msg}")
                return 'invalid'
            
            # Clean company name
            facility_data['company_name'] = FacilityValidator.clean_company_name(
                facility_data['company_name']
            )
            
            # Check for duplicates
            if await is_duplicate(
                self.db,
                facility_data['company_name'],
                facility_data['city']
            ):
                logger.debug(f"Duplicate facility: {facility_data['company_name']}")
                return 'duplicate'
            
            # Geocode if coordinates missing
            if not facility_data.get('latitude') or not facility_data.get('longitude'):
                coords = await self.geocoder.geocode(
                    facility_data['city'],
                    facility_data['state']
                )
                
                if coords:
                    facility_data['latitude'], facility_data['longitude'] = coords
                else:
                    # Try fallback coordinates
                    fallback = get_fallback_coordinates(facility_data['city'])
                    if fallback:
                        facility_data['latitude'], facility_data['longitude'] = fallback
                    else:
                        logger.warning(f"No coordinates for {facility_data['city']}")
                        # Set to None - will still insert but won't show on map
                        facility_data['latitude'] = None
                        facility_data['longitude'] = None
            
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
                "contact_email": facility_data.get('contact_email'),
                "website": facility_data.get('website'),
                "date_added": datetime.now(timezone.utc).isoformat()
            }
            
            # Insert into database
            await self.db.industrial_facilities.insert_one(facility)
            logger.info(f"Inserted facility: {facility_data['company_name']}")
            
            # Update source health with insertion count
            if 'data_source' in facility_data:
                source_name = facility_data['data_source'].replace('Demo: ', '').replace('Production: ', '')
                # This will be tracked at source level
            
            return 'inserted'
        
        except Exception as e:
            logger.error(f"Error processing facility {facility_data.get('company_name')}: {str(e)}")
            return 'invalid'

