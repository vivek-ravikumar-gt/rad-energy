# RAD Automated Discovery Pipeline

## Overview
The RAD platform now includes an automated facility discovery pipeline that continuously grows the industrial facility database without manual data entry.

## Features

### 1. **Demo Mode Crawlers**
- District Industries Centre (Tamil Nadu)
- SIPCOT Industrial Parks
- IndiaMART Manufacturing Directory
- Tiruppur Exporters Association
- KIADB Industrial Estates

Discovers realistic sample facilities from major industrial clusters:
- Tiruppur Textile Hub
- Coimbatore Foundry Cluster
- Sriperumbudur Electronics SEZ
- Hosur Automotive Hub
- Peenya Industrial Area

### 2. **Real Web Crawler Framework**
Ready-to-use framework for scraping actual websites:
- BeautifulSoup-based HTML parsing
- Configurable CSS selectors
- Async crawling with aiohttp
- Error handling and retry logic

To add real sources, configure via API:
```json
{
  "name": "SIPCOT Company Listings",
  "type": "estate_listing",
  "url": "https://sipcot.tn.gov.in/companies",
  "selectors": {
    "container": "div.company-list-item",
    "name": ".company-name",
    "industry": ".industry-type",
    "location": ".company-location"
  },
  "enabled": true
}
```

### 3. **Automated Scheduler**
- **Weekly Schedule**: Runs every Monday at 2:00 AM
- **Daily Option**: Available via API
- **Custom Schedules**: Support for cron expressions
- Auto-starts on server startup

### 4. **Smart Processing**
- **Duplicate Detection**: Fuzzy matching prevents duplicate entries
- **Automatic Estimation**: 
  - Power demand based on industry benchmarks
  - Rooftop solar potential using typical factory sizes
  - Opportunity score calculation
- **Cluster Assignment**: Auto-assigns facilities to industrial clusters

### 5. **Discovery Dashboard**
- Real-time scheduler status
- Manual discovery trigger
- Discovery history with logs
- Source configuration viewer
- Statistics and metrics

## API Endpoints

### Run Discovery Manually
```bash
POST /api/discovery/run
{
  "mode": "demo"  # or "real"
}
```

### Get Discovery Status
```bash
GET /api/discovery/status
```

### Get Discovery Logs
```bash
GET /api/discovery/logs?limit=10
```

### Start Scheduler
```bash
POST /api/discovery/scheduler/start?schedule=weekly
```

### Stop Scheduler
```bash
POST /api/discovery/scheduler/stop
```

### Get Discovery Sources
```bash
GET /api/discovery/sources
```

## Architecture

### Backend Modules
```
/app/backend/discovery/
├── __init__.py
├── crawler_base.py       # Base crawler class
├── demo_crawler.py       # Demo mode with sample data
├── real_crawler.py       # Real web scraper framework
├── estimator.py          # Power demand & solar potential estimation
├── deduplicator.py       # Duplicate detection logic
├── pipeline.py           # Main discovery orchestrator
└── scheduler.py          # APScheduler integration
```

### Data Flow
1. **Crawl** → Sources are crawled based on configuration
2. **Extract** → Company name, industry, location, cluster
3. **Estimate** → Power demand, rooftop area, solar capacity
4. **Deduplicate** → Check for existing facilities
5. **Insert** → Add new facilities to database
6. **Log** → Record discovery run details

## Discovery Sources

### Current Demo Sources
1. **District Industries Centre - Tamil Nadu**
   - Type: cluster_directory
   - Industries: Textiles, Foundries, Electronics
   - Clusters: Tiruppur, Coimbatore, Sriperumbudur

2. **SIPCOT Industrial Parks**
   - Type: estate_listing
   - Parks: Irungattukottai, Perundurai, Gangaikondan
   - Industries: Automotive, Electronics, Pharmaceuticals

3. **IndiaMART Manufacturing Directory**
   - Type: company_directory
   - Categories: Engineering, Chemicals, Plastics, Textiles

4. **Tiruppur Exporters Association**
   - Type: cluster_directory
   - Focus: Textile and garment manufacturers

5. **KIADB Industrial Estates**
   - Type: estate_listing
   - Locations: Whitefield, Peenya, Electronic City
   - Industries: Electronics, Pharmaceuticals, Engineering

## Estimation Logic

### Power Demand Benchmarks (MW)
- Textile Manufacturing: 2-3 MW
- Electronics Manufacturing: 4-6 MW
- Steel/Metal Processing: 6-10 MW
- Chemical Plants: 8-15 MW
- Automotive Manufacturing: 5-8 MW
- Warehouse/Logistics: 1-2 MW

### Rooftop Area Estimates (sq ft)
- Large facilities: 60,000-100,000 sq ft
- Medium facilities: 40,000-60,000 sq ft
- Small facilities: 30,000-45,000 sq ft

### Solar Capacity Formula
```
Solar Capacity (kW) = (Rooftop Area sq ft / 10,000) × 90 kW
```

### Opportunity Score (0-100)
- Power demand: 40 points
- Solar potential: 30 points
- Industry energy intensity: 20 points
- Cluster presence: 10 points

## Usage

### Manual Discovery
1. Navigate to "Discovery" page
2. Select mode (Demo/Real)
3. Click "Run Discovery"
4. View results in Discovery History

### Automated Discovery
- Scheduler runs weekly by default
- Check next run time in Dashboard
- Stop/Start scheduler as needed

### Monitoring
- Discovery logs show:
  - Facilities discovered
  - Facilities inserted
  - Duplicates skipped
  - Sources crawled
  - Duration

## Configuration

### Adding Real Sources
To add real web sources, insert into MongoDB:
```javascript
db.discovery_sources.insertOne({
  name: "Your Source Name",
  type: "cluster_directory", // or estate_listing, company_directory
  url: "https://example.com/listings",
  selectors: {
    container: "div.listing",
    name: ".company-name",
    industry: ".industry",
    location: ".location"
  },
  enabled: true
})
```

### Changing Schedule
Modify scheduler frequency via API:
- `daily` - Every day at 2 AM
- `weekly` - Every Monday at 2 AM
- Custom cron: `0 3 * * 2` (Tuesday 3 AM)

## Benefits

1. **Continuous Growth**: Database automatically grows with new facilities
2. **No Manual Work**: Eliminates CSV imports and manual data entry
3. **Always Fresh**: Regular updates keep data current
4. **Smart Deduplication**: Avoids duplicate entries
5. **Ready for Scale**: Framework ready for real data sources
6. **Transparent**: Full logs and monitoring

## Next Steps

### To Enable Real Crawling:
1. Identify target websites
2. Analyze HTML structure
3. Configure CSS selectors
4. Test with single source
5. Enable in production

### Potential Sources:
- Government industrial directories
- State industrial corporation websites
- Industry association member lists
- Business directory platforms
- Industrial park company listings

## Technical Details

### Dependencies
- `beautifulsoup4` - HTML parsing
- `aiohttp` - Async HTTP client
- `apscheduler` - Task scheduling
- `motor` - Async MongoDB driver

### Database Collections
- `industrial_facilities` - Main facility data
- `discovery_logs` - Discovery run history
- `discovery_sources` - Source configurations

### Scheduler
- Uses APScheduler with AsyncIO
- Runs in background without blocking
- Persists across server restarts
- Graceful shutdown handling
