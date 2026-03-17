"""Real web crawler framework for actual data sources"""
import aiohttp
import asyncio
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import logging
from .crawler_base import BaseCrawler

logger = logging.getLogger(__name__)

class RealCrawler(BaseCrawler):
    """Real web crawler for scraping actual websites"""
    
    def __init__(
        self,
        source_name: str,
        source_type: str,
        url: str,
        selectors: Dict[str, str],
        headers: Optional[Dict] = None
    ):
        super().__init__(source_name, source_type)
        self.url = url
        self.selectors = selectors  # CSS selectors for company name, industry, location
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    async def crawl(self) -> List[Dict]:
        """Crawl the website and extract facility data"""
        facilities = []
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.url,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status != 200:
                        logger.error(f"Failed to fetch {self.url}: Status {response.status}")
                        self.error_count += 1
                        return []
                    
                    html = await response.text()
                    facilities = self._parse_html(html)
                    self.discovered_count = len(facilities)
                    logger.info(f"Real crawler found {len(facilities)} facilities from {self.source_name}")
        
        except asyncio.TimeoutError:
            logger.error(f"Timeout while fetching {self.url}")
            self.error_count += 1
        except Exception as e:
            logger.error(f"Error crawling {self.url}: {str(e)}")
            self.error_count += 1
        
        return facilities
    
    def _parse_html(self, html: str) -> List[Dict]:
        """Parse HTML and extract facility information"""
        soup = BeautifulSoup(html, 'html.parser')
        facilities = []
        
        try:
            # Find all company entries using the container selector
            entries = soup.select(self.selectors.get('container', 'div.company-listing'))
            
            for entry in entries:
                try:
                    # Extract company name
                    name_elem = entry.select_one(self.selectors.get('name', '.company-name'))
                    if not name_elem:
                        continue
                    company_name = name_elem.get_text(strip=True)
                    
                    # Extract industry type
                    industry_elem = entry.select_one(self.selectors.get('industry', '.industry'))
                    raw_industry = industry_elem.get_text(strip=True) if industry_elem else 'General Manufacturing'
                    industry_type = self.normalize_industry_type(raw_industry)
                    
                    # Extract location
                    location_elem = entry.select_one(self.selectors.get('location', '.location'))
                    location = location_elem.get_text(strip=True) if location_elem else ''
                    
                    # Parse city and state from location
                    city, state = self._parse_location(location)
                    
                    if not city or not company_name:
                        continue
                    
                    # Assign cluster
                    cluster = self.extract_cluster_name(location, city)
                    
                    facilities.append({
                        'company_name': company_name,
                        'industry_type': industry_type,
                        'city': city,
                        'state': state or 'Unknown',
                        'industrial_cluster': cluster,
                        'data_source': f'Real: {self.source_name}',
                        'latitude': None,
                        'longitude': None
                    })
                
                except Exception as e:
                    logger.warning(f"Error parsing entry: {str(e)}")
                    continue
        
        except Exception as e:
            logger.error(f"Error parsing HTML: {str(e)}")
        
        return facilities
    
    def _parse_location(self, location: str) -> tuple:
        """Parse location string to extract city and state"""
        # Handle common formats: "City, State" or "City - State" or "City"
        parts = location.replace('-', ',').split(',')
        
        city = parts[0].strip() if parts else ''
        state = parts[1].strip() if len(parts) > 1 else 'Tamil Nadu'  # Default state
        
        return city, state

# Example configuration for real sources (to be configured via API)
REAL_SOURCE_TEMPLATES = [
    {
        'name': 'SIPCOT Company Listings',
        'type': 'estate_listing',
        'url': 'https://example.com/sipcot-companies',  # Placeholder
        'selectors': {
            'container': 'div.company-list-item',
            'name': '.company-name',
            'industry': '.industry-type',
            'location': '.company-location'
        },
        'enabled': False  # Disabled until real URLs are provided
    },
    {
        'name': 'IndiaMART Manufacturers',
        'type': 'company_directory',
        'url': 'https://example.com/manufacturers',  # Placeholder
        'selectors': {
            'container': 'div.manufacturer-card',
            'name': 'h3.company-title',
            'industry': 'span.category',
            'location': 'p.address'
        },
        'enabled': False
    }
]
