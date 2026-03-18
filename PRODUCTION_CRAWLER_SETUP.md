# RAD Production Crawler Setup Guide

## Overview
This guide helps you configure and enable real web crawlers for production facility discovery in RAD.

## Production Sources Available

RAD comes pre-configured with 12 production-ready source templates:

### Manufacturing Directories (3)
1. **IndiaMART - Textile Manufacturing**
2. **IndiaMART - Engineering & Machinery**
3. **IndiaMART - Chemical & Pharmaceuticals**
4. **TradeIndia - Manufacturing Directory**

### Industrial Estate Listings (6)
5. **SIPCOT - Irungattukottai Industrial Park**
6. **SIPCOT - Sriperumbudur Industrial Park**
7. **SIPCOT - Oragadam Industrial Park**
8. **SIPCOT - Hosur Industrial Park**
9. **KIADB - Peenya Industrial Area**
10. **KIADB - Hardware Park Whitefield**

### Industry Associations (2)
11. **Tiruppur Exporters Association**
12. **CODISSIA - Coimbatore**

## Quick Start

### 1. Load Production Sources
```bash
# Via UI: Go to Sources → Click "Load Production Sources"
# Via API:
curl -X POST https://your-domain.com/api/discovery/sources/seed-production
```

### 2. Test Individual Sources
Before enabling, test each source:
```bash
curl -X POST https://your-domain.com/api/discovery/sources/{source-name}/test
```

### 3. Configure CSS Selectors
Each source needs correct CSS selectors. Use browser DevTools:

1. Open target website
2. Press F12 to open DevTools
3. Use Inspector to identify elements
4. Test selectors in Console:
```javascript
document.querySelectorAll('div.listing-card')
```

### 4. Enable Sources
Once tested, enable via:
- **UI**: Toggle switch on each source
- **API**: `PUT /api/discovery/sources/{name}` with `{"enabled": true}`

### 5. Run Discovery
```bash
# Manual run with real sources
curl -X POST https://your-domain.com/api/discovery/run \
  -H "Content-Type: application/json" \
  -d '{"mode": "real"}'
```

## Detailed Configuration

### IndiaMART Setup

**Example URL**: `https://dir.indiamart.com/impcat/textile-machinery.html`

**Recommended Selectors**:
```json
{
  "container": "div.listing-card, div.ou-pro-list",
  "name": "h3, h4, .company-name",
  "industry": ".category, .business-type",
  "location": ".location, .address, .city"
}
```

**Steps**:
1. Visit category page
2. Inspect listing cards
3. Find repeating container class
4. Identify company name heading
5. Locate category/industry field
6. Find location/address element

**Considerations**:
- IndiaMART uses dynamic loading (JavaScript)
- May require handling pagination
- Rate limit: ~10 requests/minute recommended
- Check robots.txt

### SIPCOT Setup

**Example URL**: `https://sipcotweb.tn.gov.in/industrial-parks/irungattukottai`

**Recommended Selectors**:
```json
{
  "container": "div.company-list, table tr",
  "name": ".company-name, td:nth-child(1)",
  "industry": ".industry-type, td:nth-child(2)",
  "location": ".location, td:nth-child(3)"
}
```

**Important Notes**:
- Official SIPCOT directories may require authentication
- Consider requesting official data export
- Check data.gov.in for open datasets
- Respect government website policies

**Alternative Approach**:
Contact SIPCOT directly:
```
Email: info@sipcot.com
Phone: +91-44-2220-0405
Request: Company directory data access
```

### KIADB Setup

**Example URL**: `https://kiadb.karnataka.gov.in/industrial-areas/peenya`

**Recommended Selectors**:
```json
{
  "container": "div.company-list, table tr",
  "name": ".company-name, td:nth-child(1)",
  "industry": ".industry-type, td:nth-child(2)",
  "location": ".location"
}
```

**Best Practices**:
- Check if API access available
- Look for open data portals
- Consider official data request
- Karnataka open data: data.karnataka.gov.in

### Industry Association Setup

**Considerations**:
- Most require membership
- Some have public directories
- May offer CSV/Excel exports
- Contact for data sharing agreement

**Example Request Template**:
```
Subject: Data Sharing Request for Renewable Energy Initiative

Dear [Association Name],

We are developing RAD, a renewable energy opportunity platform 
to help manufacturers transition to solar power. We would like 
to access your member directory to identify potential renewable 
energy adoption opportunities.

Purpose: Facilitate renewable energy transitions
Benefit: Help members reduce electricity costs
Data Usage: Company name, industry, location only

Would you be open to sharing this data or providing API access?

Best regards,
[Your Name]
```

## Production Checklist

### Before Enabling Sources

- [ ] **Legal Review**
  - Check website Terms of Service
  - Review robots.txt file
  - Ensure no copyright violations
  - Get permission if required

- [ ] **Technical Testing**
  - Test CSS selectors on live page
  - Verify data extraction accuracy
  - Check for JavaScript-rendered content
  - Test with various page layouts
  - Handle pagination if needed

- [ ] **Rate Limiting**
  - Identify acceptable request rate
  - Implement 2-5 second delays
  - Monitor for 429 errors
  - Use exponential backoff

- [ ] **Error Handling**
  - Test network failure scenarios
  - Handle missing data gracefully
  - Implement retry logic
  - Log all errors

- [ ] **Data Quality**
  - Validate company names
  - Check industry classification
  - Verify location parsing
  - Test deduplication

### Monitoring in Production

- [ ] **Daily Checks**
  - Review discovery logs
  - Check success rates
  - Monitor error patterns
  - Verify data quality

- [ ] **Weekly Review**
  - Analyze facilities discovered
  - Check for duplicates
  - Review failed sources
  - Adjust selectors if needed

- [ ] **Monthly Audit**
  - Evaluate source performance
  - Update configurations
  - Add new sources
  - Remove inactive sources

## Advanced Features

### Custom Rate Limiting

Modify crawler delay:
```python
# In production_crawler.py
crawler = ProductionCrawler(
    source_name,
    source_type,
    url,
    selectors,
    max_retries=3,
    rate_limit_delay=5.0  # 5 seconds between requests
)
```

### Custom Headers

Add authentication or custom headers:
```json
{
  "name": "Custom Source",
  "url": "https://example.com",
  "headers": {
    "Authorization": "Bearer your-token",
    "X-Custom-Header": "value"
  }
}
```

### Pagination Support

For multi-page directories:
```python
# Extend ProductionCrawler to handle pagination
async def crawl_paginated(self, max_pages=5):
    all_facilities = []
    for page in range(1, max_pages + 1):
        url = f"{self.url}?page={page}"
        facilities = await self.fetch_and_parse(url)
        all_facilities.extend(facilities)
        await asyncio.sleep(self.rate_limit_delay)
    return all_facilities
```

## Troubleshooting

### Common Issues

**Issue**: No facilities found
**Solution**: 
- Verify CSS selectors using browser DevTools
- Check if page uses JavaScript rendering
- Inspect network requests for API calls

**Issue**: Rate limited (429 errors)
**Solution**:
- Increase `rate_limit_delay`
- Reduce concurrent requests
- Add User-Agent rotation

**Issue**: Access forbidden (403)
**Solution**:
- Check if authentication required
- Verify User-Agent header
- Consider requesting official access

**Issue**: Incorrect data extracted
**Solution**:
- Re-inspect HTML structure
- Update CSS selectors
- Handle multiple selector fallbacks

### Testing Selectors

Use browser console:
```javascript
// Test container selector
console.log(document.querySelectorAll('div.listing-card').length);

// Test company name extraction
document.querySelectorAll('div.listing-card').forEach(card => {
  console.log(card.querySelector('h3').textContent);
});
```

## API Reference

### Get All Sources
```
GET /api/discovery/sources
```

### Create Source
```
POST /api/discovery/sources
Body: {
  "name": "Source Name",
  "type": "company_directory",
  "url": "https://example.com",
  "selectors": {...},
  "enabled": false
}
```

### Update Source
```
PUT /api/discovery/sources/{name}
Body: {"enabled": true}
```

### Test Source
```
POST /api/discovery/sources/{name}/test
Response: {
  "status": "success",
  "facilities_found": 25,
  "sample_facilities": [...]
}
```

### Delete Source
```
DELETE /api/discovery/sources/{name}
```

## Best Practices

1. **Start with Demo Mode**
   - Test pipeline with demo sources
   - Verify deduplication logic
   - Check data quality

2. **Enable Sources Gradually**
   - Start with 1-2 sources
   - Monitor for issues
   - Scale up slowly

3. **Regular Monitoring**
   - Check logs daily
   - Review data quality
   - Adjust as needed

4. **Respect Website Policies**
   - Follow robots.txt
   - Implement rate limiting
   - Get permission when possible

5. **Data Quality First**
   - Validate all extracted data
   - Implement strict deduplication
   - Review facilities regularly

6. **Official APIs Preferred**
   - Always check for official APIs
   - Request data access formally
   - Consider data partnerships

## Support

For issues or questions:
- Check `/app/DISCOVERY_PIPELINE.md`
- Review discovery logs
- Test individual sources
- Contact data source providers

## Production Schedule

**Recommended Schedule**:
- Daily: Incremental updates from fastest sources
- Weekly: Full crawl of all sources
- Monthly: Deep validation and cleanup

**Configure via API**:
```bash
# Daily at 2 AM
curl -X POST https://your-domain.com/api/discovery/scheduler/start?schedule=daily

# Weekly on Monday
curl -X POST https://your-domain.com/api/discovery/scheduler/start?schedule=weekly
```

## Next Steps

1. Load production sources
2. Test 1-2 sources thoroughly
3. Enable tested sources
4. Run manual discovery
5. Monitor results
6. Enable more sources
7. Set up automated schedule
8. Regular monitoring and maintenance
