"""Enhanced validation for facility data with strict rules"""
import re
import logging
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)

# Generic terms that require valid suffix to be accepted
GENERIC_TERMS = [
    'supplier', 'suppliers',
    'manufacturer', 'manufacturers',
    'exporter', 'exporters',
    'directory', 'directories',
    'best', 'top', 'leading',
    'global', 'international',
    'wholesale', 'wholesaler',
    'trader', 'traders',
    'dealer', 'dealers',
    'distributor', 'distributors',
    'company', 'companies',
    'list', 'listing',
]

# Valid company suffixes that legitimize otherwise generic names
VALID_SUFFIXES = [
    r'ltd\.?$',
    r'limited$',
    r'pvt\.?\s*ltd\.?$',
    r'private\s+limited$',
    r'industries$',
    r'engineering$',
    r'mills$',
    r'textiles$',
    r'corporation$',
    r'corp\.?$',
    r'inc\.?$',
    r'incorporated$',
    r'works$',
    r'foundry$',
    r'manufacturing$',
    r'enterprises$',
    r'solutions$',
    r'technologies$',
    r'systems$',
]

# Invalid company name patterns (always reject)
INVALID_PATTERNS = [
    r'^test',
    r'^demo',
    r'^sample',
    r'^example',
    r'^placeholder',
    r'^abc\s+company',
    r'^company\s+name',
    r'^\d+$',  # Just numbers
    r'^[a-z]$',  # Single letter
    r'^n/?a$',  # N/A
    r'^null$',
    r'^none$',
    r'^unknown$',
    r'^\s*$',  # Empty or whitespace only
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
    """Validator for facility data quality with strict rules"""
    
    @staticmethod
    def validate_company_name(name: str) -> Tuple[bool, Optional[str]]:
        """Validate company name with strict rules
        
        Returns:
            (is_valid, error_message)
        """
        if not name or len(name.strip()) < 3:
            return (False, "Company name too short")
        
        name_clean = name.strip()
        name_lower = name_clean.lower()
        
        # Check against invalid patterns
        for pattern in INVALID_PATTERNS:
            if re.search(pattern, name_lower, re.IGNORECASE):
                return (False, f"Invalid pattern: {pattern}")
        
        # Must contain at least one letter
        if not re.search(r'[a-zA-Z]', name):
            return (False, "No letters in company name")
        
        # Check for generic terms
        contains_generic = any(term in name_lower for term in GENERIC_TERMS)
        
        if contains_generic:
            # Check if it has a valid suffix
            has_valid_suffix = any(
                re.search(pattern, name_lower, re.IGNORECASE) 
                for pattern in VALID_SUFFIXES
            )
            
            if not has_valid_suffix:
                return (False, f"Generic name without valid suffix: {name}")
        
        # Reject if only generic terms (like "Suppliers Directory")
        words = name_lower.split()
        non_generic_words = [w for w in words if w not in GENERIC_TERMS and len(w) > 2]
        
        if len(non_generic_words) == 0:
            return (False, "Only generic terms in name")
        
        return (True, None)
    
    @staticmethod
    def validate_city(city: str) -> Tuple[bool, Optional[str]]:
        """Validate city name
        
        Returns:
            (is_valid, error_message)
        """
        if not city or len(city.strip()) < 2:
            return (False, "City missing or too short")
        
        # Must contain only letters, spaces, and hyphens
        if not re.match(r'^[a-zA-Z\s\-]+$', city.strip()):
            return (False, "City contains invalid characters")
        
        return (True, None)
    
    @staticmethod
    def validate_industry(industry: str) -> Tuple[bool, Optional[str]]:
        """Validate industry is manufacturing/industrial
        
        Returns:
            (is_valid, error_message)
        """
        if not industry:
            return (False, "Industry missing")
        
        if industry not in VALID_INDUSTRIES:
            return (False, f"Industry not in valid list: {industry}")
        
        return (True, None)
    
    @staticmethod
    def validate_facility(facility_data: Dict) -> Tuple[bool, Optional[str]]:
        """Validate complete facility data - ALL fields required
        
        Returns:
            (is_valid, error_message)
        """
        # ALL three fields are REQUIRED
        if not facility_data.get('company_name'):
            return (False, "Company name missing")
        
        if not facility_data.get('city'):
            return (False, "City missing")
        
        if not facility_data.get('industry_type'):
            return (False, "Industry type missing")
        
        # Validate company name
        is_valid, error = FacilityValidator.validate_company_name(facility_data['company_name'])
        if not is_valid:
            return (False, f"Invalid company name: {error}")
        
        # Validate city
        is_valid, error = FacilityValidator.validate_city(facility_data['city'])
        if not is_valid:
            return (False, f"Invalid city: {error}")
        
        # Validate industry
        is_valid, error = FacilityValidator.validate_industry(facility_data['industry_type'])
        if not is_valid:
            return (False, f"Invalid industry: {error}")
        
        # Validate state (optional but recommended)
        if not facility_data.get('state'):
            logger.warning(f"State missing for {facility_data['company_name']}")
        
        return (True, None)
    
    @staticmethod
    def is_generic_entry(company_name: str) -> bool:
        """Check if an entry is generic and should be removed
        
        This is used for database cleanup
        """
        is_valid, _ = FacilityValidator.validate_company_name(company_name)
        return not is_valid
    
    @staticmethod
    def clean_company_name(name: str) -> str:
        """Clean and normalize company name"""
        # Remove extra whitespace
        name = ' '.join(name.split())
        
        # Remove leading/trailing punctuation
        name = name.strip('.,;:!?-_')
        
        # Capitalize properly
        name = name.strip()
        
        return name
