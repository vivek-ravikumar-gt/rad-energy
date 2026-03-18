"""Enhanced production crawler with retry logic and rate limiting"""
import aiohttp
import asyncio
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import logging
import random
from datetime import datetime
from .crawler_base import BaseCrawler

logger = logging.getLogger(__name__)

class ProductionCrawler(BaseCrawler):
    """Production-ready web crawler with advanced features"""
    
    def __init__(
        self,
        source_name: str,
        source_type: str,
        url: str,
        selectors: Dict[str, str],
        headers: Optional[Dict] = None,
        max_retries: int = 3,
        rate_limit_delay: float = 2.0
    ):
        super().__init__(source_name, source_type)
        self.url = url
        self.selectors = selectors
        self.max_retries = max_retries
        self.rate_limit_delay = rate_limit_delay
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
    
    async def crawl(self) -> List[Dict]:
        """Crawl with retry logic and rate limiting"""
        for attempt in range(self.max_retries):
            try:
                # Rate limiting
                if attempt > 0:
                    delay = self.rate_limit_delay * (2 ** attempt) + random.uniform(0, 1)
                    logger.info(f"Retry {attempt + 1}/{self.max_retries} after {delay:.1f}s delay")
                    await asyncio.sleep(delay)
                
                facilities = await self._fetch_and_parse()
                self.discovered_count = len(facilities)
                logger.info(f"Production crawler found {len(facilities)} facilities from {self.source_name}")
                return facilities
            
            except asyncio.TimeoutError:
                logger.warning(f"Timeout on attempt {attempt + 1}/{self.max_retries} for {self.url}")
                self.error_count += 1
                if attempt == self.max_retries - 1:
                    return []
            
            except aiohttp.ClientError as e:
                logger.warning(f"Client error on attempt {attempt + 1}/{self.max_retries}: {str(e)}")
                self.error_count += 1
                if attempt == self.max_retries - 1:
                    return []
            
            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt + 1}/{self.max_retries}: {str(e)}")
                self.error_count += 1
                if attempt == self.max_retries - 1:
                    return []
        
        return []
    
    async def _fetch_and_parse(self) -> List[Dict]:
        """Fetch HTML and parse facilities"""
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(self.url, headers=self.headers) as response:
                if response.status == 429:  # Too Many Requests
                    raise aiohttp.ClientError("Rate limited by server")
                
                if response.status == 403:  # Forbidden
                    raise aiohttp.ClientError("Access forbidden - may need authentication")
                
                if response.status != 200:
                    raise aiohttp.ClientError(f"HTTP {response.status}")
                
                html = await response.text()
                return self._parse_html(html)
    
    def _parse_html(self, html: str) -> List[Dict]:
        """Parse HTML and extract facility information"""
        soup = BeautifulSoup(html, 'html.parser')
        facilities = []
        
        try:
            # Find all company entries
            container_selector = self.selectors.get('container', 'div.listing')
            entries = soup.select(container_selector)
            
            if not entries:
                logger.warning(f"No entries found with selector: {container_selector}")
                return []
            
            logger.info(f"Found {len(entries)} entries to process")
            
            for idx, entry in enumerate(entries):
                try:
                    facility = self._extract_facility_data(entry)
                    if facility and facility.get('company_name'):
                        facilities.append(facility)
                
                except Exception as e:
                    logger.warning(f"Error parsing entry {idx}: {str(e)}")
                    continue
        
        except Exception as e:
            logger.error(f"Error parsing HTML: {str(e)}")
        
        return facilities
    
    def _extract_facility_data(self, entry) -> Optional[Dict]:
        """Extract facility data from a single entry - ALL fields required"""
        # Extract company name - try multiple selectors
        name_selector = self.selectors.get('name', '.company-name')
        name_elem = entry.select_one(name_selector)
        if not name_elem:
            return None
        company_name = name_elem.get_text(strip=True)
        
        # Extract industry type - REQUIRED
        industry_selector = self.selectors.get('industry', '.industry')
        industry_elem = entry.select_one(industry_selector)
        raw_industry = industry_elem.get_text(strip=True) if industry_elem else None
        if not raw_industry:
            logger.debug(f"Skipping entry with no industry: {company_name}")
            return None
        industry_type = self.normalize_industry_type(raw_industry)
        
        # Extract location - REQUIRED
        location_selector = self.selectors.get('location', '.location')
        location_elem = entry.select_one(location_selector)
        location = location_elem.get_text(strip=True) if location_elem else ''
        
        # Parse city and state
        city, state = self._parse_location(location)
        
        # ALL three required fields MUST be present
        if not city or not company_name or not industry_type:
            logger.debug(f"Skipping entry missing required fields: company={company_name}, city={city}, industry={industry_type}")
            return None
        
        # Extract cluster if available
        cluster_selector = self.selectors.get('cluster')
        if cluster_selector:
            cluster_elem = entry.select_one(cluster_selector)
            cluster = cluster_elem.get_text(strip=True) if cluster_elem else self.extract_cluster_name(location, city)
        else:
            cluster = self.extract_cluster_name(location, city)
        
        # Extract website if available
        website_selector = self.selectors.get('website')
        website = None
        if website_selector:
            website_elem = entry.select_one(website_selector)
            if website_elem:
                if website_elem.get('href'):
                    website = website_elem.get('href')
                else:
                    website = website_elem.get_text(strip=True)
        
        return {
            'company_name': company_name,
            'industry_type': industry_type,
            'city': city,
            'state': state or 'India',
            'industrial_cluster': cluster,
            'website': website,
            'data_source': f'Production: {self.source_name}',
            'latitude': None,
            'longitude': None
        }
    
    def _parse_location(self, location: str) -> tuple:
        """Parse location string to extract city and state"""
        if not location:
            return ('', '')
        
        # Handle various formats
        location = location.replace('|', ',').replace('-', ',')
        parts = [p.strip() for p in location.split(',') if p.strip()]
        
        city = parts[0] if parts else ''
        state = parts[1] if len(parts) > 1 else 'Tamil Nadu'
        
        return (city, state)
