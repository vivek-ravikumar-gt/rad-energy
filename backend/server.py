from fastapi import FastAPI, APIRouter, HTTPException, Query, BackgroundTasks
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
from emergentintegrations.llm.chat import LlmChat, UserMessage

# Import discovery modules
from discovery.pipeline import DiscoveryPipeline
from discovery.scheduler import DiscoveryScheduler

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Initialize discovery scheduler
discovery_scheduler = DiscoveryScheduler(db)

# Industry power demand benchmarks (in MW)
INDUSTRY_BENCHMARKS = {
    "Textile Manufacturing": {"min": 2, "max": 3},
    "Electronics Manufacturing": {"min": 4, "max": 6},
    "Warehouse/Logistics": {"min": 1, "max": 2},
    "Steel/Metal Processing": {"min": 6, "max": 10},
    "Chemical Plants": {"min": 8, "max": 15},
    "Automotive Manufacturing": {"min": 5, "max": 8},
    "Foundry": {"min": 3, "max": 5},
    "Engineering/Machinery": {"min": 2, "max": 4},
}

# Models
class IndustrialFacility(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    company_name: str
    industry_type: str
    city: str
    state: str
    industrial_cluster: str
    estimated_power_demand_mw: float
    rooftop_area_sqft: int
    estimated_solar_capacity_kw: float
    renewable_opportunity_score: int
    existing_renewable_adoption: bool = False
    contact_email: Optional[str] = None
    website: Optional[str] = None
    data_source: str = "Manual Entry"
    date_added: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class FacilityCreate(BaseModel):
    company_name: str
    industry_type: str
    city: str
    state: str
    industrial_cluster: str
    rooftop_area_sqft: int
    existing_renewable_adoption: bool = False
    contact_email: Optional[str] = None
    website: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class FacilityUpdate(BaseModel):
    company_name: Optional[str] = None
    industry_type: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    industrial_cluster: Optional[str] = None
    rooftop_area_sqft: Optional[int] = None
    existing_renewable_adoption: Optional[bool] = None
    contact_email: Optional[str] = None
    website: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class EmailGenerateRequest(BaseModel):
    facility_id: str

class EmailGenerateResponse(BaseModel):
    email_content: str
    facility_name: str

class ClusterStats(BaseModel):
    cluster_name: str
    city: str
    state: str
    company_count: int
    total_power_demand_mw: float
    total_solar_potential_kw: float
    avg_opportunity_score: float

class DashboardStats(BaseModel):
    total_facilities: int
    total_solar_potential_kw: float
    total_power_demand_mw: float
    avg_opportunity_score: float
    facilities_with_renewable: int

# Utility Functions
def calculate_power_demand(industry_type: str) -> float:
    """Estimate power demand based on industry type"""
    import random
    benchmark = INDUSTRY_BENCHMARKS.get(industry_type, {"min": 2, "max": 4})
    return round(random.uniform(benchmark["min"], benchmark["max"]), 2)

def calculate_solar_capacity(rooftop_area_sqft: int) -> float:
    """Calculate solar capacity: 10,000 sq ft ≈ 90 kW"""
    return round((rooftop_area_sqft / 10000) * 90, 2)

def calculate_opportunity_score(
    power_demand_mw: float,
    solar_capacity_kw: float,
    industry_type: str,
    has_cluster: bool
) -> int:
    """Calculate renewable opportunity score (0-100)"""
    score = 0
    
    # Power demand contribution (0-40 points)
    score += min(power_demand_mw * 4, 40)
    
    # Solar potential contribution (0-30 points)
    score += min(solar_capacity_kw / 10, 30)
    
    # Industry energy intensity (0-20 points)
    high_energy_industries = ["Steel/Metal Processing", "Chemical Plants", "Electronics Manufacturing"]
    if industry_type in high_energy_industries:
        score += 20
    else:
        score += 10
    
    # Cluster presence (0-10 points)
    if has_cluster:
        score += 10
    
    return min(int(score), 100)

# API Routes
@api_router.get("/")
async def root():
    return {"message": "RAD - Renewable Acquisition & Discovery API"}

@api_router.post("/facilities", response_model=IndustrialFacility)
async def create_facility(facility_input: FacilityCreate):
    """Create a new industrial facility"""
    # Calculate derived fields
    power_demand = calculate_power_demand(facility_input.industry_type)
    solar_capacity = calculate_solar_capacity(facility_input.rooftop_area_sqft)
    opportunity_score = calculate_opportunity_score(
        power_demand,
        solar_capacity,
        facility_input.industry_type,
        bool(facility_input.industrial_cluster)
    )
    
    facility_data = facility_input.model_dump()
    facility_data["estimated_power_demand_mw"] = power_demand
    facility_data["estimated_solar_capacity_kw"] = solar_capacity
    facility_data["renewable_opportunity_score"] = opportunity_score
    
    facility = IndustrialFacility(**facility_data)
    
    doc = facility.model_dump()
    doc['date_added'] = doc['date_added'].isoformat()
    
    await db.industrial_facilities.insert_one(doc)
    return facility

@api_router.get("/facilities", response_model=List[IndustrialFacility])
async def get_facilities(
    city: Optional[str] = None,
    industry_type: Optional[str] = None,
    cluster: Optional[str] = None,
    min_demand: Optional[float] = None,
    max_demand: Optional[float] = None,
    min_solar: Optional[float] = None,
    max_solar: Optional[float] = None,
    min_score: Optional[int] = None,
    limit: int = Query(100, le=500)
):
    """Get facilities with optional filters"""
    query = {}
    
    if city:
        query["city"] = {"$regex": city, "$options": "i"}
    if industry_type:
        query["industry_type"] = {"$regex": industry_type, "$options": "i"}
    if cluster:
        query["industrial_cluster"] = {"$regex": cluster, "$options": "i"}
    if min_demand is not None:
        query["estimated_power_demand_mw"] = query.get("estimated_power_demand_mw", {})
        query["estimated_power_demand_mw"]["$gte"] = min_demand
    if max_demand is not None:
        query["estimated_power_demand_mw"] = query.get("estimated_power_demand_mw", {})
        query["estimated_power_demand_mw"]["$lte"] = max_demand
    if min_solar is not None:
        query["estimated_solar_capacity_kw"] = query.get("estimated_solar_capacity_kw", {})
        query["estimated_solar_capacity_kw"]["$gte"] = min_solar
    if max_solar is not None:
        query["estimated_solar_capacity_kw"] = query.get("estimated_solar_capacity_kw", {})
        query["estimated_solar_capacity_kw"]["$lte"] = max_solar
    if min_score is not None:
        query["renewable_opportunity_score"] = {"$gte": min_score}
    
    facilities = await db.industrial_facilities.find(query, {"_id": 0}).limit(limit).to_list(limit)
    
    for facility in facilities:
        if isinstance(facility['date_added'], str):
            facility['date_added'] = datetime.fromisoformat(facility['date_added'])
    
    return facilities

@api_router.get("/facilities/{facility_id}", response_model=IndustrialFacility)
async def get_facility(facility_id: str):
    """Get a single facility by ID"""
    facility = await db.industrial_facilities.find_one({"id": facility_id}, {"_id": 0})
    
    if not facility:
        raise HTTPException(status_code=404, detail="Facility not found")
    
    if isinstance(facility['date_added'], str):
        facility['date_added'] = datetime.fromisoformat(facility['date_added'])
    
    return facility

@api_router.patch("/facilities/{facility_id}", response_model=IndustrialFacility)
async def update_facility(facility_id: str, update_data: FacilityUpdate):
    """Update a facility"""
    facility = await db.industrial_facilities.find_one({"id": facility_id}, {"_id": 0})
    
    if not facility:
        raise HTTPException(status_code=404, detail="Facility not found")
    
    update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
    
    # Recalculate derived fields if relevant data changed
    if "rooftop_area_sqft" in update_dict:
        update_dict["estimated_solar_capacity_kw"] = calculate_solar_capacity(update_dict["rooftop_area_sqft"])
    
    if "industry_type" in update_dict or "rooftop_area_sqft" in update_dict:
        industry = update_dict.get("industry_type", facility["industry_type"])
        power_demand = calculate_power_demand(industry)
        update_dict["estimated_power_demand_mw"] = power_demand
        
        solar_capacity = update_dict.get("estimated_solar_capacity_kw", facility["estimated_solar_capacity_kw"])
        cluster = update_dict.get("industrial_cluster", facility["industrial_cluster"])
        update_dict["renewable_opportunity_score"] = calculate_opportunity_score(
            power_demand, solar_capacity, industry, bool(cluster)
        )
    
    await db.industrial_facilities.update_one({"id": facility_id}, {"$set": update_dict})
    
    updated_facility = await db.industrial_facilities.find_one({"id": facility_id}, {"_id": 0})
    if isinstance(updated_facility['date_added'], str):
        updated_facility['date_added'] = datetime.fromisoformat(updated_facility['date_added'])
    
    return updated_facility

@api_router.delete("/facilities/{facility_id}")
async def delete_facility(facility_id: str):
    """Delete a facility"""
    result = await db.industrial_facilities.delete_one({"id": facility_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Facility not found")
    
    return {"message": "Facility deleted successfully"}

@api_router.get("/facilities/top/prospects", response_model=List[IndustrialFacility])
async def get_top_prospects(limit: int = Query(10, le=50)):
    """Get top renewable prospects ranked by opportunity score"""
    facilities = await db.industrial_facilities.find(
        {},
        {"_id": 0}
    ).sort("renewable_opportunity_score", -1).limit(limit).to_list(limit)
    
    for facility in facilities:
        if isinstance(facility['date_added'], str):
            facility['date_added'] = datetime.fromisoformat(facility['date_added'])
    
    return facilities

@api_router.get("/clusters", response_model=List[ClusterStats])
async def get_cluster_stats():
    """Get aggregated statistics by industrial cluster"""
    pipeline = [
        {
            "$group": {
                "_id": {
                    "cluster": "$industrial_cluster",
                    "city": "$city",
                    "state": "$state"
                },
                "company_count": {"$sum": 1},
                "total_power_demand_mw": {"$sum": "$estimated_power_demand_mw"},
                "total_solar_potential_kw": {"$sum": "$estimated_solar_capacity_kw"},
                "avg_opportunity_score": {"$avg": "$renewable_opportunity_score"}
            }
        },
        {
            "$project": {
                "_id": 0,
                "cluster_name": "$_id.cluster",
                "city": "$_id.city",
                "state": "$_id.state",
                "company_count": 1,
                "total_power_demand_mw": {"$round": ["$total_power_demand_mw", 2]},
                "total_solar_potential_kw": {"$round": ["$total_solar_potential_kw", 2]},
                "avg_opportunity_score": {"$round": ["$avg_opportunity_score", 0]}
            }
        },
        {"$sort": {"total_power_demand_mw": -1}}
    ]
    
    clusters = await db.industrial_facilities.aggregate(pipeline).to_list(100)
    return clusters

@api_router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    """Get overall dashboard statistics"""
    pipeline = [
        {
            "$group": {
                "_id": None,
                "total_facilities": {"$sum": 1},
                "total_solar_potential_kw": {"$sum": "$estimated_solar_capacity_kw"},
                "total_power_demand_mw": {"$sum": "$estimated_power_demand_mw"},
                "avg_opportunity_score": {"$avg": "$renewable_opportunity_score"},
                "facilities_with_renewable": {
                    "$sum": {"$cond": ["$existing_renewable_adoption", 1, 0]}
                }
            }
        }
    ]
    
    result = await db.industrial_facilities.aggregate(pipeline).to_list(1)
    
    if not result:
        return DashboardStats(
            total_facilities=0,
            total_solar_potential_kw=0,
            total_power_demand_mw=0,
            avg_opportunity_score=0,
            facilities_with_renewable=0
        )
    
    stats = result[0]
    return DashboardStats(
        total_facilities=stats["total_facilities"],
        total_solar_potential_kw=round(stats["total_solar_potential_kw"], 2),
        total_power_demand_mw=round(stats["total_power_demand_mw"], 2),
        avg_opportunity_score=round(stats["avg_opportunity_score"], 0),
        facilities_with_renewable=stats["facilities_with_renewable"]
    )

@api_router.post("/email/generate", response_model=EmailGenerateResponse)
async def generate_outreach_email(request: EmailGenerateRequest):
    """Generate AI-powered outreach email for a facility"""
    facility = await db.industrial_facilities.find_one({"id": request.facility_id}, {"_id": 0})
    
    if not facility:
        raise HTTPException(status_code=404, detail="Facility not found")
    
    # Calculate potential savings (assuming ₹6/kWh industrial rate)
    solar_capacity_kw = facility["estimated_solar_capacity_kw"]
    annual_generation_kwh = solar_capacity_kw * 1400  # ~1400 hours equivalent/year
    annual_savings = annual_generation_kwh * 6
    
    # Calculate carbon reduction (0.82 kg CO2 per kWh)
    carbon_reduction_tons = (annual_generation_kwh * 0.82) / 1000
    
    prompt = f"""Generate a professional cold outreach email for a renewable energy sales pitch.

Company: {facility['company_name']}
Industry: {facility['industry_type']}
Location: {facility['city']}, {facility['state']}
Estimated Electricity Demand: {facility['estimated_power_demand_mw']} MW
Estimated Solar Capacity Potential: {solar_capacity_kw} kW
Estimated Annual Electricity Cost Savings: ₹{annual_savings:,.0f}
Estimated Annual Carbon Reduction: {carbon_reduction_tons:.1f} tons CO2

Write a compelling, personalized email that:
1. Introduces our renewable energy consulting services
2. Highlights their specific electricity demand and solar potential
3. Mentions the cost savings opportunity
4. Emphasizes the environmental impact
5. Includes a clear call-to-action for a consultation
6. Keeps a professional yet approachable tone
7. Keep it concise (under 200 words)

Do not include subject line. Start directly with the greeting."""
    
    try:
        # Initialize LLM Chat
        chat = LlmChat(
            api_key=os.environ.get('EMERGENT_LLM_KEY'),
            session_id=f"email-gen-{request.facility_id}",
            system_message="You are a professional renewable energy sales consultant writing personalized outreach emails."
        ).with_model("openai", "gpt-5.2")
        
        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        return EmailGenerateResponse(
            email_content=response,
            facility_name=facility['company_name']
        )
    except Exception as e:
        logger.error(f"Error generating email: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate email: {str(e)}")

@api_router.post("/seed-data")
async def seed_initial_data():
    """Seed the database with initial industrial facility data"""
    # Check if data already exists
    count = await db.industrial_facilities.count_documents({})
    if count > 0:
        return {"message": f"Database already has {count} facilities. Skipping seed."}
    
    # Sample facilities from major industrial clusters
    sample_facilities = [
        # Tiruppur - Textiles
        {"company_name": "Tiruppur Textiles Ltd", "industry_type": "Textile Manufacturing", "city": "Tiruppur", "state": "Tamil Nadu", "industrial_cluster": "Tiruppur Textile Hub", "rooftop_area_sqft": 50000, "latitude": 11.1075, "longitude": 77.3398},
        {"company_name": "Cottex Garments", "industry_type": "Textile Manufacturing", "city": "Tiruppur", "state": "Tamil Nadu", "industrial_cluster": "Tiruppur Textile Hub", "rooftop_area_sqft": 35000, "latitude": 11.0945, "longitude": 77.3507},
        {"company_name": "Rainbow Knitwear", "industry_type": "Textile Manufacturing", "city": "Tiruppur", "state": "Tamil Nadu", "industrial_cluster": "Tiruppur Textile Hub", "rooftop_area_sqft": 42000, "latitude": 11.1168, "longitude": 77.3440, "existing_renewable_adoption": True},
        
        # Coimbatore - Foundries
        {"company_name": "Precision Castings India", "industry_type": "Foundry", "city": "Coimbatore", "state": "Tamil Nadu", "industrial_cluster": "Coimbatore Foundry Cluster", "rooftop_area_sqft": 38000, "latitude": 11.0168, "longitude": 76.9558},
        {"company_name": "Kovai Metal Works", "industry_type": "Steel/Metal Processing", "city": "Coimbatore", "state": "Tamil Nadu", "industrial_cluster": "Coimbatore Foundry Cluster", "rooftop_area_sqft": 55000, "latitude": 10.9925, "longitude": 76.9620},
        {"company_name": "South India Forgings", "industry_type": "Foundry", "city": "Coimbatore", "state": "Tamil Nadu", "industrial_cluster": "Coimbatore Foundry Cluster", "rooftop_area_sqft": 45000, "latitude": 11.0084, "longitude": 76.9756},
        
        # Sriperumbudur - Electronics
        {"company_name": "TechCircuit Electronics", "industry_type": "Electronics Manufacturing", "city": "Sriperumbudur", "state": "Tamil Nadu", "industrial_cluster": "Sriperumbudur Electronics SEZ", "rooftop_area_sqft": 75000, "latitude": 12.9713, "longitude": 79.9445},
        {"company_name": "Digital Components India", "industry_type": "Electronics Manufacturing", "city": "Sriperumbudur", "state": "Tamil Nadu", "industrial_cluster": "Sriperumbudur Electronics SEZ", "rooftop_area_sqft": 82000, "latitude": 12.9654, "longitude": 79.9525, "existing_renewable_adoption": True},
        {"company_name": "Semiconductor Solutions", "industry_type": "Electronics Manufacturing", "city": "Sriperumbudur", "state": "Tamil Nadu", "industrial_cluster": "Sriperumbudur Electronics SEZ", "rooftop_area_sqft": 95000, "latitude": 12.9768, "longitude": 79.9387},
        
        # Hosur - Automotive
        {"company_name": "Hosur Auto Components", "industry_type": "Automotive Manufacturing", "city": "Hosur", "state": "Tamil Nadu", "industrial_cluster": "Hosur Automotive Hub", "rooftop_area_sqft": 65000, "latitude": 12.7409, "longitude": 77.8253},
        {"company_name": "Velocity Motors Pvt Ltd", "industry_type": "Automotive Manufacturing", "city": "Hosur", "state": "Tamil Nadu", "industrial_cluster": "Hosur Automotive Hub", "rooftop_area_sqft": 72000, "latitude": 12.7274, "longitude": 77.8387},
        {"company_name": "Precision Auto Parts", "industry_type": "Automotive Manufacturing", "city": "Hosur", "state": "Tamil Nadu", "industrial_cluster": "Hosur Automotive Hub", "rooftop_area_sqft": 58000, "latitude": 12.7551, "longitude": 77.8195, "existing_renewable_adoption": True},
        
        # Peenya - Engineering
        {"company_name": "Bangalore Machine Tools", "industry_type": "Engineering/Machinery", "city": "Bangalore", "state": "Karnataka", "industrial_cluster": "Peenya Industrial Area", "rooftop_area_sqft": 48000, "latitude": 13.0317, "longitude": 77.5199},
        {"company_name": "Karnataka Engineering Works", "industry_type": "Engineering/Machinery", "city": "Bangalore", "state": "Karnataka", "industrial_cluster": "Peenya Industrial Area", "rooftop_area_sqft": 52000, "latitude": 13.0385, "longitude": 77.5267},
        {"company_name": "Peenya Hydraulics", "industry_type": "Engineering/Machinery", "city": "Bangalore", "state": "Karnataka", "industrial_cluster": "Peenya Industrial Area", "rooftop_area_sqft": 44000, "latitude": 13.0254, "longitude": 77.5142},
        
        # Additional facilities
        {"company_name": "ChemTech Industries", "industry_type": "Chemical Plants", "city": "Chennai", "state": "Tamil Nadu", "industrial_cluster": "Manali Industrial Estate", "rooftop_area_sqft": 88000, "latitude": 13.1647, "longitude": 80.2622},
        {"company_name": "LogiHub Warehousing", "industry_type": "Warehouse/Logistics", "city": "Chennai", "state": "Tamil Nadu", "industrial_cluster": "Oragadam Logistics Park", "rooftop_area_sqft": 120000, "latitude": 12.8247, "longitude": 79.9897},
        {"company_name": "Southern Steel Mills", "industry_type": "Steel/Metal Processing", "city": "Salem", "state": "Tamil Nadu", "industrial_cluster": "Salem Steel Hub", "rooftop_area_sqft": 95000, "latitude": 11.6643, "longitude": 78.1460, "existing_renewable_adoption": True},
        {"company_name": "Apex Electronics", "industry_type": "Electronics Manufacturing", "city": "Bangalore", "state": "Karnataka", "industrial_cluster": "Whitefield Electronics Zone", "rooftop_area_sqft": 68000, "latitude": 12.9698, "longitude": 77.7500},
        {"company_name": "MetroParts Auto", "industry_type": "Automotive Manufacturing", "city": "Chennai", "state": "Tamil Nadu", "industrial_cluster": "Ambattur Industrial Estate", "rooftop_area_sqft": 61000, "latitude": 13.0980, "longitude": 80.1620},
    ]
    
    created_facilities = []
    for facility_data in sample_facilities:
        facility_input = FacilityCreate(**facility_data)
        
        # Calculate derived fields
        power_demand = calculate_power_demand(facility_input.industry_type)
        solar_capacity = calculate_solar_capacity(facility_input.rooftop_area_sqft)
        opportunity_score = calculate_opportunity_score(
            power_demand,
            solar_capacity,
            facility_input.industry_type,
            bool(facility_input.industrial_cluster)
        )
        
        facility_dict = facility_input.model_dump()
        facility_dict["estimated_power_demand_mw"] = power_demand
        facility_dict["estimated_solar_capacity_kw"] = solar_capacity
        facility_dict["renewable_opportunity_score"] = opportunity_score
        
        facility = IndustrialFacility(**facility_dict)
        doc = facility.model_dump()
        doc['date_added'] = doc['date_added'].isoformat()
        
        await db.industrial_facilities.insert_one(doc)
        created_facilities.append(facility.company_name)
    
    return {
        "message": f"Successfully seeded {len(created_facilities)} facilities",
        "facilities": created_facilities
    }


# Discovery API Endpoints
class DiscoveryRunRequest(BaseModel):
    mode: str = "demo"  # 'demo' or 'real'

class DiscoveryStatusResponse(BaseModel):
    scheduler_running: bool
    next_run: Optional[str] = None
    last_run: Optional[dict] = None

@api_router.post("/discovery/run")
async def run_discovery_manually(request: DiscoveryRunRequest, background_tasks: BackgroundTasks):
    """Manually trigger discovery pipeline"""
    try:
        # Run discovery in background
        pipeline = DiscoveryPipeline(db, mode=request.mode)
        background_tasks.add_task(pipeline.run_discovery)
        
        return {
            "status": "started",
            "message": f"Discovery pipeline started in {request.mode} mode",
            "mode": request.mode
        }
    except Exception as e:
        logger.error(f"Error starting discovery: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/discovery/status", response_model=DiscoveryStatusResponse)
async def get_discovery_status():
    """Get discovery scheduler status and last run info"""
    scheduler_status = discovery_scheduler.get_status()
    
    # Get last discovery log
    last_log = await db.discovery_logs.find_one(
        {},
        {"_id": 0},
        sort=[("start_time", -1)]
    )
    
    return {
        "scheduler_running": scheduler_status['is_running'],
        "next_run": scheduler_status['jobs'][0]['next_run'] if scheduler_status['jobs'] else None,
        "last_run": last_log
    }

@api_router.get("/discovery/logs")
async def get_discovery_logs(limit: int = Query(10, le=50)):
    """Get discovery run logs"""
    logs = await db.discovery_logs.find(
        {},
        {"_id": 0}
    ).sort("start_time", -1).limit(limit).to_list(limit)
    
    return logs

@api_router.post("/discovery/scheduler/start")
async def start_discovery_scheduler(schedule: str = Query("weekly")):
    """Start automated discovery scheduler"""
    try:
        discovery_scheduler.start(schedule)
        return {
            "status": "started",
            "message": f"Scheduler started with {schedule} schedule",
            "schedule": schedule
        }
    except Exception as e:
        logger.error(f"Error starting scheduler: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/discovery/scheduler/stop")
async def stop_discovery_scheduler():
    """Stop automated discovery scheduler"""
    try:
        discovery_scheduler.stop()
        return {
            "status": "stopped",
            "message": "Scheduler stopped successfully"
        }
    except Exception as e:
        logger.error(f"Error stopping scheduler: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/discovery/sources")
async def get_discovery_sources():
    """Get configured discovery sources"""
    sources = await db.discovery_sources.find({}, {"_id": 0}).to_list(100)
    
    # If no sources configured, return demo sources
    if not sources:
        from discovery.demo_crawler import DEMO_SOURCES
        return {"sources": DEMO_SOURCES, "mode": "demo"}
    
    return {"sources": sources, "mode": "configured"}

@api_router.post("/discovery/sources")
async def create_discovery_source(source: dict):
    """Create a new discovery source"""
    try:
        # Add timestamp
        source["created_at"] = datetime.now(timezone.utc).isoformat()
        source["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        await db.discovery_sources.insert_one(source)
        return {"status": "success", "message": "Source created successfully"}
    except Exception as e:
        logger.error(f"Error creating source: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/discovery/sources/{source_name}")
async def update_discovery_source(source_name: str, updates: dict):
    """Update a discovery source"""
    try:
        updates["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        result = await db.discovery_sources.update_one(
            {"name": source_name},
            {"$set": updates}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Source not found")
        
        return {"status": "success", "message": "Source updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating source: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/discovery/sources/{source_name}")
async def delete_discovery_source(source_name: str):
    """Delete a discovery source"""
    try:
        result = await db.discovery_sources.delete_one({"name": source_name})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Source not found")
        
        return {"status": "success", "message": "Source deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting source: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/discovery/sources/{source_name}/test")
async def test_discovery_source(source_name: str):
    """Test a single discovery source"""
    try:
        source = await db.discovery_sources.find_one({"name": source_name}, {"_id": 0})
        
        if not source:
            raise HTTPException(status_code=404, detail="Source not found")
        
        from discovery.production_crawler import ProductionCrawler
        
        crawler = ProductionCrawler(
            source["name"],
            source["type"],
            source["url"],
            source["selectors"]
        )
        
        facilities = await crawler.crawl()
        
        return {
            "status": "success",
            "facilities_found": len(facilities),
            "sample_facilities": facilities[:3] if facilities else [],
            "errors": crawler.error_count
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing source: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/discovery/sources/seed-production")
async def seed_production_sources():
    """Seed database with production source configurations"""
    try:
        from discovery.production_sources import PRODUCTION_SOURCES
        
        # Check if already seeded
        count = await db.discovery_sources.count_documents({})
        if count > 0:
            return {
                "status": "skipped",
                "message": f"Database already has {count} sources"
            }
        
        # Insert production sources
        for source in PRODUCTION_SOURCES:
            source["created_at"] = datetime.now(timezone.utc).isoformat()
            source["updated_at"] = datetime.now(timezone.utc).isoformat()
            await db.discovery_sources.insert_one(source)
        
        return {
            "status": "success",
            "message": f"Seeded {len(PRODUCTION_SOURCES)} production sources",
            "count": len(PRODUCTION_SOURCES)
        }
    except Exception as e:
        logger.error(f"Error seeding sources: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_discovery_scheduler():
    """Start discovery scheduler on app startup"""
    # Start weekly automated discovery
    discovery_scheduler.start(schedule='weekly')
    logger.info("Discovery scheduler started on app startup")

@app.on_event("shutdown")
async def shutdown_db_client():
    discovery_scheduler.stop()
    client.close()