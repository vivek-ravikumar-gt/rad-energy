"""Base crawler class for facility discovery"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

class BaseCrawler(ABC):
    """Base class for all crawlers"""
    
    def __init__(self, source_name: str, source_type: str):
        self.source_name = source_name
        self.source_type = source_type  # 'cluster_directory', 'estate_listing', 'company_directory'
        self.discovered_count = 0
        self.error_count = 0
        self.start_time = None
        self.end_time = None
    
    @abstractmethod
    async def crawl(self) -> List[Dict]:
        """Crawl the source and return list of discovered facilities"""
        pass
    
    def normalize_industry_type(self, raw_industry: str) -> str:
        """Normalize industry type to match our categories"""
        industry_mapping = {
            'textile': 'Textile Manufacturing',
            'cotton': 'Cotton Spinning',
            'garment': 'Garment Manufacturing',
            'apparel': 'Garment Manufacturing',
            'electronics': 'Electronics Manufacturing',
            'semiconductor': 'Semiconductor Manufacturing',
            'warehouse': 'Warehouse/Logistics',
            'logistics': 'Warehouse/Logistics',
            'steel': 'Steel/Metal Processing',
            'metal': 'Steel/Metal Processing',
            'chemical': 'Chemical Plants',
            'pharma': 'Pharmaceutical Manufacturing',
            'pharmaceutical': 'Pharmaceutical Manufacturing',
            'automotive': 'Automotive Manufacturing',
            'auto': 'Auto Components',
            'foundry': 'Foundry',
            'engineering': 'Engineering/Machinery',
            'machinery': 'Engineering/Machinery',
            'food': 'Food Processing',
            'plastic': 'Plastics Manufacturing',
            'packaging': 'Packaging',
        }
        
        raw_lower = raw_industry.lower()
        for key, value in industry_mapping.items():
            if key in raw_lower:
                return value
        
        return 'Engineering/Machinery'  # Default
    
    def extract_cluster_name(self, location: str, city: str) -> Optional[str]:
        """Extract or assign industrial cluster name"""
        cluster_keywords = {
            'tiruppur': 'Tiruppur Textile Hub',
            'coimbatore': 'Coimbatore Foundry Cluster',
            'sriperumbudur': 'Sriperumbudur Electronics SEZ',
            'hosur': 'Hosur Automotive Hub',
            'peenya': 'Peenya Industrial Area',
            'bangalore': 'Peenya Industrial Area',
            'chennai': 'Ambattur Industrial Estate',
            'ambattur': 'Ambattur Industrial Estate',
            'salem': 'Salem Steel Hub',
            'vellore': 'Vellore Leather Cluster',
            'erode': 'Erode Textile Cluster',
            'karur': 'Karur Textile Park',
            'madurai': 'Madurai Industrial Estate',
            'trichy': 'Trichy Engineering Cluster',
            'oragadam': 'Oragadam Auto Cluster',
            'sipcot': 'SIPCOT Industrial Park',
            'kiadb': 'KIADB Industrial Estate',
        }
        
        location_lower = location.lower()
        city_lower = city.lower()
        
        for keyword, cluster in cluster_keywords.items():
            if keyword in location_lower or keyword in city_lower:
                return cluster
        
        # Default cluster based on city
        return f"{city} Industrial Area"
    
    def create_log_entry(self, status: str, message: str, facilities_found: int = 0) -> Dict:
        """Create a discovery log entry"""
        return {
            "source_name": self.source_name,
            "source_type": self.source_type,
            "status": status,  # 'success', 'error', 'partial'
            "message": message,
            "facilities_found": facilities_found,
            "timestamp": datetime.now(timezone.utc)
        }
