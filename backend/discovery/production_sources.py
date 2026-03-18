"""Production-ready source configurations for real web crawling"""

# Real source configurations based on research
# These configurations are ready to use but should be tested and adjusted

PRODUCTION_SOURCES = [
    # IndiaMART Manufacturing Directory
    {
        "name": "IndiaMART - Textile Manufacturing",
        "type": "company_directory",
        "url": "https://dir.indiamart.com/impcat/textile-machinery.html",
        "selectors": {
            "container": "div.listing-card, div.ou-pro-list",
            "name": "h3, h4, .company-name",
            "industry": ".category, .business-type",
            "location": ".location, .address, .city"
        },
        "enabled": False,  # Enable after testing
        "notes": "IndiaMART textile manufacturing listings. Test selectors on live page."
    },
    {
        "name": "IndiaMART - Engineering & Machinery",
        "type": "company_directory",
        "url": "https://dir.indiamart.com/impcat/engineering-goods.html",
        "selectors": {
            "container": "div.listing-card, div.ou-pro-list",
            "name": "h3, h4",
            "industry": ".category",
            "location": ".location, .city"
        },
        "enabled": False,
        "notes": "IndiaMART engineering goods directory"
    },
    {
        "name": "IndiaMART - Chemical & Pharmaceuticals",
        "type": "company_directory",
        "url": "https://dir.indiamart.com/impcat/chemicals.html",
        "selectors": {
            "container": "div.listing-card",
            "name": "h3, h4",
            "industry": ".category",
            "location": ".location"
        },
        "enabled": False,
        "notes": "Chemical and pharmaceutical manufacturers"
    },
    
    # TradeIndia Manufacturing Directory
    {
        "name": "TradeIndia - Manufacturing Directory",
        "type": "company_directory",
        "url": "https://www.tradeindia.com/manufacturers/",
        "selectors": {
            "container": "div.company-list-item, div.seller-card",
            "name": ".company-title, h3",
            "industry": ".category, .business-type",
            "location": ".location, .address"
        },
        "enabled": False,
        "notes": "TradeIndia manufacturing directory. Requires selector testing."
    },
    
    # SIPCOT Industrial Parks
    {
        "name": "SIPCOT - Irungattukottai Industrial Park",
        "type": "estate_listing",
        "url": "https://sipcotweb.tn.gov.in/industrial-parks/irungattukottai",
        "selectors": {
            "container": "div.company-list, table tr",
            "name": ".company-name, td:nth-child(1)",
            "industry": ".industry-type, td:nth-child(2)",
            "location": ".location, td:nth-child(3)",
            "cluster": ".park-name"
        },
        "enabled": False,
        "cluster_default": "SIPCOT Irungattukottai Industrial Park",
        "notes": "SIPCOT official directory. Check if public access available."
    },
    {
        "name": "SIPCOT - Sriperumbudur Industrial Park",
        "type": "estate_listing",
        "url": "https://sipcotweb.tn.gov.in/industrial-parks/sriperumbudur",
        "selectors": {
            "container": "div.company-list, table tr",
            "name": ".company-name, td:nth-child(1)",
            "industry": ".industry-type, td:nth-child(2)",
            "location": ".location"
        },
        "enabled": False,
        "cluster_default": "SIPCOT Sriperumbudur Industrial Park",
        "notes": "Electronics and automotive cluster"
    },
    {
        "name": "SIPCOT - Oragadam Industrial Park",
        "type": "estate_listing",
        "url": "https://sipcotweb.tn.gov.in/industrial-parks/oragadam",
        "selectors": {
            "container": "div.company-list, table tr",
            "name": ".company-name, td:nth-child(1)",
            "industry": ".industry-type",
            "location": ".location"
        },
        "enabled": False,
        "cluster_default": "SIPCOT Oragadam Auto Cluster",
        "notes": "Major automotive manufacturing hub"
    },
    {
        "name": "SIPCOT - Hosur Industrial Park",
        "type": "estate_listing",
        "url": "https://sipcotweb.tn.gov.in/industrial-parks/hosur",
        "selectors": {
            "container": "div.company-list, table tr",
            "name": ".company-name, td:nth-child(1)",
            "industry": ".industry-type",
            "location": ".location"
        },
        "enabled": False,
        "cluster_default": "SIPCOT Hosur Industrial Estate",
        "notes": "Automotive and electronics manufacturing"
    },
    
    # KIADB Industrial Estates
    {
        "name": "KIADB - Peenya Industrial Area",
        "type": "estate_listing",
        "url": "https://kiadb.karnataka.gov.in/industrial-areas/peenya",
        "selectors": {
            "container": "div.company-list, table tr",
            "name": ".company-name, td:nth-child(1)",
            "industry": ".industry-type, td:nth-child(2)",
            "location": ".location"
        },
        "enabled": False,
        "cluster_default": "KIADB Peenya Industrial Area",
        "notes": "Bangalore's largest industrial area"
    },
    {
        "name": "KIADB - Hardware Park Whitefield",
        "type": "estate_listing",
        "url": "https://kiadb.karnataka.gov.in/industrial-areas/hardware-park",
        "selectors": {
            "container": "div.company-list, table tr",
            "name": ".company-name, td:nth-child(1)",
            "industry": ".industry-type",
            "location": ".location"
        },
        "enabled": False,
        "cluster_default": "KIADB Hardware Park Whitefield",
        "notes": "Electronics and hardware manufacturing"
    },
    
    # Industry Association Directories
    {
        "name": "Tiruppur Exporters Association",
        "type": "cluster_directory",
        "url": "https://www.teaonline.in/members",  # Placeholder - verify actual URL
        "selectors": {
            "container": "div.member-list, table tr",
            "name": ".member-name, td:nth-child(1)",
            "industry": ".business-type",
            "location": ".location"
        },
        "enabled": False,
        "cluster_default": "Tiruppur Textile Hub",
        "notes": "Textile and garment exporters. Verify member directory URL."
    },
    {
        "name": "CODISSIA - Coimbatore",
        "type": "cluster_directory",
        "url": "https://www.codissia.com/members",  # Placeholder
        "selectors": {
            "container": "div.member-list",
            "name": ".company-name",
            "industry": ".industry",
            "location": ".location"
        },
        "enabled": False,
        "cluster_default": "Coimbatore Industrial Cluster",
        "notes": "Coimbatore District Small Industries Association. Check member access."
    }
]

# Configuration instructions for each source type
SOURCE_SETUP_INSTRUCTIONS = {
    "indiamart": """
    IndiaMART Setup:
    1. Visit the category page (e.g., /impcat/textile-machinery.html)
    2. Open browser DevTools (F12)
    3. Identify the listing container (usually div with class like 'listing-card')
    4. Find company name selector (usually h3 or h4)
    5. Find category/industry selector
    6. Find location selector
    7. Test selectors in console: document.querySelectorAll('your-selector')
    8. Update selectors in configuration
    9. Note: May require handling pagination for multiple pages
    """,
    
    "sipcot": """
    SIPCOT Setup:
    1. Contact SIPCOT for official company directory access
    2. Some parks may have public company lists
    3. Alternative: Use government data portals (data.gov.in)
    4. Check robots.txt before crawling
    5. Respect rate limits
    """,
    
    "kiadb": """
    KIADB Setup:
    1. Visit KIADB official website
    2. Check if company listings are publicly available
    3. May require authentication or permission
    4. Consider requesting official data export
    5. Check data.karnataka.gov.in for open data
    """,
    
    "associations": """
    Industry Association Setup:
    1. Most require membership for full directory access
    2. Some have public member listings
    3. Contact association for data sharing
    4. May provide CSV/Excel exports
    5. Check if API access available
    """
}

# Testing checklist before enabling sources
TESTING_CHECKLIST = """
Before enabling a source for production:

1. Legal & Ethical
   - Review website Terms of Service
   - Check robots.txt compliance
   - Ensure no copyright violations
   - Get permission if required

2. Technical Testing
   - Test selectors on live page
   - Verify data extraction quality
   - Check for dynamic content (JavaScript rendering)
   - Test pagination handling
   - Measure response times

3. Rate Limiting
   - Identify acceptable request frequency
   - Implement delays between requests
   - Monitor for rate limit errors (429)
   - Add exponential backoff

4. Data Quality
   - Verify company names are accurate
   - Check industry type extraction
   - Validate location parsing
   - Test deduplication logic

5. Error Handling
   - Test with network failures
   - Handle missing data gracefully
   - Log errors properly
   - Implement retry logic

6. Production Monitoring
   - Set up alerting for failures
   - Monitor success rates
   - Track data quality metrics
   - Review logs regularly
"""
