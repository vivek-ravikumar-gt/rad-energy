"""Geocoding service for converting city names to coordinates"""
import aiohttp
import asyncio
import logging
from typing import Optional, Tuple
import hashlib
import json
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class GeocodingService:
    """Geocoding service using Nominatim (OpenStreetMap)"""
    
    def __init__(self):
        self.base_url = "https://nominatim.openstreetmap.org/search"
        self.cache = {}  # Simple in-memory cache
        self.cache_duration = timedelta(days=30)
        self.rate_limit_delay = 1.0  # Nominatim requires 1 request/second
        self.last_request_time = None
    
    async def geocode(self, city: str, state: str = "India") -> Optional[Tuple[float, float]]:
        """Get coordinates for a city
        
        Returns:
            Tuple of (latitude, longitude) or None if not found
        """
        # Create cache key
        cache_key = self._get_cache_key(city, state)
        
        # Check cache
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if datetime.now() - cached_data['timestamp'] < self.cache_duration:
                logger.debug(f"Cache hit for {city}, {state}")
                return cached_data['coords']
        
        # Rate limiting
        await self._rate_limit()
        
        try:
            # Prepare query
            query = f"{city}, {state}, India"
            params = {
                'q': query,
                'format': 'json',
                'limit': 1,
                'addressdetails': 1
            }
            
            headers = {
                'User-Agent': 'RAD-RenewableDiscovery/1.0 (renewable-energy-platform)'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.base_url,
                    params=params,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data and len(data) > 0:
                            result = data[0]
                            lat = float(result['lat'])
                            lon = float(result['lon'])
                            coords = (lat, lon)
                            
                            # Cache result
                            self.cache[cache_key] = {
                                'coords': coords,
                                'timestamp': datetime.now()
                            }
                            
                            logger.info(f"Geocoded {city}, {state}: {coords}")
                            return coords
                        else:
                            logger.warning(f"No results for {city}, {state}")
                            # Cache negative result
                            self.cache[cache_key] = {
                                'coords': None,
                                'timestamp': datetime.now()
                            }
                            return None
                    else:
                        logger.error(f"Geocoding failed: HTTP {response.status}")
                        return None
        
        except asyncio.TimeoutError:
            logger.error(f"Geocoding timeout for {city}, {state}")
            return None
        except Exception as e:
            logger.error(f"Geocoding error for {city}, {state}: {str(e)}")
            return None
    
    async def batch_geocode(self, locations: list) -> dict:
        """Geocode multiple locations
        
        Args:
            locations: List of (city, state) tuples
        
        Returns:
            Dict mapping location to coordinates
        """
        results = {}
        
        for city, state in locations:
            coords = await self.geocode(city, state)
            results[(city, state)] = coords
        
        return results
    
    def _get_cache_key(self, city: str, state: str) -> str:
        """Generate cache key"""
        key_str = f"{city.lower().strip()},{state.lower().strip()}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    async def _rate_limit(self):
        """Enforce rate limiting"""
        if self.last_request_time:
            elapsed = (datetime.now() - self.last_request_time).total_seconds()
            if elapsed < self.rate_limit_delay:
                await asyncio.sleep(self.rate_limit_delay - elapsed)
        
        self.last_request_time = datetime.now()

# Fallback coordinates for major Indian cities
FALLBACK_COORDINATES = {
    'tiruppur': (11.1075, 77.3398),
    'coimbatore': (11.0168, 76.9558),
    'sriperumbudur': (12.9713, 79.9445),
    'hosur': (12.7409, 77.8253),
    'bangalore': (12.9716, 77.5946),
    'bengaluru': (12.9716, 77.5946),
    'chennai': (13.0827, 80.2707),
    'salem': (11.6643, 78.1460),
    'erode': (11.3410, 77.7172),
    'madurai': (9.9252, 78.1198),
    'trichy': (10.7905, 78.7047),
    'vellore': (12.9165, 79.1325),
    'karur': (10.9601, 78.0766),
    'puducherry': (11.9416, 79.8083),
    'hyderabad': (17.3850, 78.4867),
    'pune': (18.5204, 73.8567),
    'mumbai': (19.0760, 72.8777),
    'delhi': (28.7041, 77.1025),
    'ahmedabad': (23.0225, 72.5714),
}

def get_fallback_coordinates(city: str) -> Optional[Tuple[float, float]]:
    """Get fallback coordinates for known cities"""
    city_key = city.lower().strip()
    return FALLBACK_COORDINATES.get(city_key)
