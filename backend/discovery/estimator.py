"""Estimation logic for electricity demand and solar potential"""
import random
from typing import Dict, Tuple

# Industry power demand benchmarks (in MW)
INDUSTRY_BENCHMARKS = {
    "Textile Manufacturing": {"min": 2, "max": 3},
    "Cotton Spinning": {"min": 1.5, "max": 2.5},
    "Garment Manufacturing": {"min": 1, "max": 2},
    "Electronics Manufacturing": {"min": 4, "max": 6},
    "Semiconductor Manufacturing": {"min": 5, "max": 8},
    "Warehouse/Logistics": {"min": 1, "max": 2},
    "Steel/Metal Processing": {"min": 6, "max": 10},
    "Chemical Plants": {"min": 8, "max": 15},
    "Pharmaceutical Manufacturing": {"min": 3, "max": 5},
    "Automotive Manufacturing": {"min": 5, "max": 8},
    "Auto Components": {"min": 3, "max": 5},
    "Foundry": {"min": 3, "max": 5},
    "Engineering/Machinery": {"min": 2, "max": 4},
    "Food Processing": {"min": 2, "max": 4},
    "Plastics Manufacturing": {"min": 2, "max": 3},
    "Packaging": {"min": 1, "max": 2},
    "Default": {"min": 2, "max": 4}
}

# Typical rooftop area by industry (in sq ft)
ROOFTOP_ESTIMATES = {
    "Textile Manufacturing": {"min": 40000, "max": 60000},
    "Cotton Spinning": {"min": 35000, "max": 50000},
    "Garment Manufacturing": {"min": 30000, "max": 45000},
    "Electronics Manufacturing": {"min": 60000, "max": 90000},
    "Semiconductor Manufacturing": {"min": 70000, "max": 100000},
    "Warehouse/Logistics": {"min": 80000, "max": 150000},
    "Steel/Metal Processing": {"min": 70000, "max": 110000},
    "Chemical Plants": {"min": 60000, "max": 100000},
    "Pharmaceutical Manufacturing": {"min": 50000, "max": 75000},
    "Automotive Manufacturing": {"min": 60000, "max": 90000},
    "Auto Components": {"min": 45000, "max": 65000},
    "Foundry": {"min": 40000, "max": 60000},
    "Engineering/Machinery": {"min": 40000, "max": 60000},
    "Food Processing": {"min": 35000, "max": 55000},
    "Plastics Manufacturing": {"min": 35000, "max": 50000},
    "Packaging": {"min": 30000, "max": 45000},
    "Default": {"min": 40000, "max": 60000}
}

def estimate_power_demand(industry_type: str) -> float:
    """Estimate power demand based on industry type (in MW)"""
    benchmark = INDUSTRY_BENCHMARKS.get(industry_type, INDUSTRY_BENCHMARKS["Default"])
    return round(random.uniform(benchmark["min"], benchmark["max"]), 2)

def estimate_rooftop_area(industry_type: str) -> int:
    """Estimate rooftop area based on industry type (in sq ft)"""
    estimate = ROOFTOP_ESTIMATES.get(industry_type, ROOFTOP_ESTIMATES["Default"])
    return random.randint(estimate["min"], estimate["max"])

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
    high_energy_industries = [
        "Steel/Metal Processing", "Chemical Plants", 
        "Electronics Manufacturing", "Semiconductor Manufacturing",
        "Pharmaceutical Manufacturing"
    ]
    if industry_type in high_energy_industries:
        score += 20
    else:
        score += 10
    
    # Cluster presence (0-10 points)
    if has_cluster:
        score += 10
    
    return min(int(score), 100)

def estimate_facility_metrics(industry_type: str, cluster: str) -> Dict:
    """Estimate all facility metrics"""
    rooftop_area = estimate_rooftop_area(industry_type)
    power_demand = estimate_power_demand(industry_type)
    solar_capacity = calculate_solar_capacity(rooftop_area)
    opportunity_score = calculate_opportunity_score(
        power_demand,
        solar_capacity,
        industry_type,
        bool(cluster)
    )
    
    return {
        "rooftop_area_sqft": rooftop_area,
        "estimated_power_demand_mw": power_demand,
        "estimated_solar_capacity_kw": solar_capacity,
        "renewable_opportunity_score": opportunity_score
    }
