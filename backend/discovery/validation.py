"""Enhanced validation for facility data"""
import re
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Invalid company name patterns
INVALID_PATTERNS = [
    r'^test',
    r'^demo',
    r'^sample',
    r'^example',
    r'^placeholder',
    r'^abc\s+company',
    r'^company\s+name',
    r'\d{10,}',  # Just numbers
]

# Valid industry types (manufacturing and industrial only)
VALID_INDUSTRIES = {
    'Textile Manufacturing',
    'Cotton Spinning',
    'Garment Manufacturing',
    'Electronics Manufacturing',
    'Semiconductor Manufacturing',
    'Warehouse/Logistics',
    'Steel/Metal Processing',
    'Chemical Plants',
    'Pharmaceutical Manufacturing',
    'Automotive Manufacturing',
    'Auto Components',
    'Foundry',
    'Engineering/Machinery',
    'Food Processing',
    'Plastics Manufacturing',
    'Packaging',
}

class FacilityValidator:
    """Validator for facility data quality"""
    
    @staticmethod
    def validate_company_name(name: str) -> bool:
        """Validate company name is real and not placeholder"""
        if not name or len(name.strip()) < 3:
            logger.warning(f"Company name too short: {name}")
            return False
        
        name_lower = name.lower().strip()
        
        # Check against invalid patterns
        for pattern in INVALID_PATTERNS:
            if re.search(pattern, name_lower):
                logger.warning(f"Invalid company name pattern: {name}")
                return False
        
        # Must contain at least one letter
        if not re.search(r'[a-zA-Z]', name):
            logger.warning(f"Company name has no letters: {name}")
            return False
        
        return True
    
    @staticmethod
    def validate_city(city: str) -> bool:
        """Validate city name"""
        if not city or len(city.strip()) < 2:
            logger.warning(f"Invalid city: {city}")
            return False
        
        # Must contain only letters, spaces, and hyphens
        if not re.match(r'^[a-zA-Z\s\-]+$', city):
            logger.warning(f"City contains invalid characters: {city}")
            return False
        
        return True
    
    @staticmethod
    def validate_industry(industry: str) -> bool:
        """Validate industry is manufacturing/industrial"""
        if not industry:
            logger.warning("Industry type missing")
            return False
        
        if industry not in VALID_INDUSTRIES:
            logger.warning(f"Industry not in valid list: {industry}")
            return False
        
        return True
    
    @staticmethod
    def validate_facility(facility_data: Dict) -> tuple[bool, Optional[str]]:
        """Validate complete facility data
        
        Returns:
            (is_valid, error_message)
        """
        # Validate company name
        if not FacilityValidator.validate_company_name(facility_data.get('company_name', '')):
            return (False, "Invalid or placeholder company name")
        
        # Validate city
        if not FacilityValidator.validate_city(facility_data.get('city', '')):
            return (False, "Invalid or missing city")
        
        # Validate industry
        if not FacilityValidator.validate_industry(facility_data.get('industry_type', '')):
            return (False, "Invalid or non-manufacturing industry")
        
        # Validate state
        if not facility_data.get('state'):
            return (False, "State missing")
        
        return (True, None)
    
    @staticmethod
    def clean_company_name(name: str) -> str:
        """Clean and normalize company name"""
        # Remove extra whitespace
        name = ' '.join(name.split())
        
        # Remove common suffixes for normalization
        name = re.sub(r'\s+(Pvt\.?\s+Ltd\.?|Private Limited|Limited|Ltd\.?|Inc\.?|Corporation|Corp\.?)$', '', name, flags=re.IGNORECASE)
        
        # Capitalize properly
        name = name.strip()
        
        return name
