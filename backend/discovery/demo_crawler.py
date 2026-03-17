"""Demo crawler with realistic sample data for immediate operation"""
import asyncio
import random
from typing import List, Dict
from .crawler_base import BaseCrawler
import logging

logger = logging.getLogger(__name__)

class DemoCrawler(BaseCrawler):
    """Demo crawler that generates realistic facility data"""
    
    def __init__(self, source_name: str, source_type: str, max_facilities: int = 10):
        super().__init__(source_name, source_type)
        self.max_facilities = max_facilities
    
    async def crawl(self) -> List[Dict]:
        """Generate demo facility data"""
        facilities = []
        
        if self.source_type == 'cluster_directory':
            facilities = self._generate_cluster_facilities()
        elif self.source_type == 'estate_listing':
            facilities = self._generate_estate_facilities()
        elif self.source_type == 'company_directory':
            facilities = self._generate_company_directory_facilities()
        
        # Simulate network delay
        await asyncio.sleep(random.uniform(0.5, 1.5))
        
        self.discovered_count = len(facilities)
        logger.info(f"Demo crawler found {len(facilities)} facilities from {self.source_name}")
        
        return facilities
    
    def _generate_cluster_facilities(self) -> List[Dict]:
        """Generate facilities from cluster directories"""
        clusters_data = [
            {
                'cluster': 'Tiruppur Textile Hub',
                'city': 'Tiruppur',
                'state': 'Tamil Nadu',
                'industries': ['Textile Manufacturing', 'Cotton Spinning', 'Garment Manufacturing'],
                'companies': [
                    'Sri Krishna Textiles', 'Lakshmi Cotton Mills', 'Bhavani Spinners',
                    'Murugan Garments', 'Annamalai Textiles', 'Selvam Knitwear'
                ]
            },
            {
                'cluster': 'Coimbatore Foundry Cluster',
                'city': 'Coimbatore',
                'state': 'Tamil Nadu',
                'industries': ['Foundry', 'Steel/Metal Processing', 'Engineering/Machinery'],
                'companies': [
                    'Lakshmi Machine Works', 'PSG Foundries', 'Rane Castings',
                    'Amaravathi Forgings', 'Kumaran Castings', 'Senthil Metal Works'
                ]
            },
            {
                'cluster': 'Sriperumbudur Electronics SEZ',
                'city': 'Sriperumbudur',
                'state': 'Tamil Nadu',
                'industries': ['Electronics Manufacturing', 'Semiconductor Manufacturing', 'Auto Components'],
                'companies': [
                    'Foxconn Electronics', 'Samsung Components', 'Flextronics India',
                    'Jabil Circuits', 'Sanmina-SCI', 'Celestica Technologies'
                ]
            },
            {
                'cluster': 'Hosur Automotive Hub',
                'city': 'Hosur',
                'state': 'Tamil Nadu',
                'industries': ['Automotive Manufacturing', 'Auto Components', 'Engineering/Machinery'],
                'companies': [
                    'TVS Motor Company', 'Ashok Leyland', 'Titan Industries',
                    'BorgWarner India', 'Michelin Tyres', 'Federal-Mogul Goetze'
                ]
            },
            {
                'cluster': 'Peenya Industrial Area',
                'city': 'Bangalore',
                'state': 'Karnataka',
                'industries': ['Engineering/Machinery', 'Electronics Manufacturing', 'Auto Components'],
                'companies': [
                    'Bharat Electronics', 'HMT Machine Tools', 'Bosch India',
                    'Microchip Technology', 'Parker Hannifin', 'GE Healthcare'
                ]
            }
        ]
        
        facilities = []
        selected_clusters = random.sample(clusters_data, min(3, len(clusters_data)))
        
        for cluster_data in selected_clusters:
            num_companies = random.randint(2, min(4, len(cluster_data['companies'])))
            selected_companies = random.sample(cluster_data['companies'], num_companies)
            
            for company in selected_companies:
                if len(facilities) >= self.max_facilities:
                    break
                
                facilities.append({
                    'company_name': company,
                    'industry_type': random.choice(cluster_data['industries']),
                    'city': cluster_data['city'],
                    'state': cluster_data['state'],
                    'industrial_cluster': cluster_data['cluster'],
                    'data_source': f'Demo: {self.source_name}',
                    'latitude': self._get_coordinates(cluster_data['city'])[0],
                    'longitude': self._get_coordinates(cluster_data['city'])[1]
                })
        
        return facilities[:self.max_facilities]
    
    def _generate_estate_facilities(self) -> List[Dict]:
        """Generate facilities from industrial estate listings"""
        estates_data = [
            {
                'estate': 'SIPCOT Irungattukottai',
                'city': 'Sriperumbudur',
                'state': 'Tamil Nadu',
                'industries': ['Automotive Manufacturing', 'Electronics Manufacturing', 'Pharmaceutical Manufacturing'],
                'companies': [
                    'Renault-Nissan Alliance', 'Daimler India', 'Nokia Networks',
                    'Pfizer Ltd', 'Orchid Pharma', 'Caterpillar India'
                ]
            },
            {
                'estate': 'KIADB Whitefield',
                'city': 'Bangalore',
                'state': 'Karnataka',
                'industries': ['Electronics Manufacturing', 'Pharmaceutical Manufacturing', 'Engineering/Machinery'],
                'companies': [
                    'Oracle India', 'Philips Electronics', 'Wipro Technologies',
                    'Biocon Ltd', 'Strides Pharma', 'ABB India'
                ]
            },
            {
                'estate': 'SIPCOT Perundurai',
                'city': 'Erode',
                'state': 'Tamil Nadu',
                'industries': ['Textile Manufacturing', 'Chemical Plants', 'Plastics Manufacturing'],
                'companies': [
                    'KPR Mill', 'Eastman Exports', 'Clariant Chemicals',
                    'Precot Meridian', 'Bannari Amman Textiles', 'Jayashree Textiles'
                ]
            }
        ]
        
        facilities = []
        selected_estates = random.sample(estates_data, min(2, len(estates_data)))
        
        for estate_data in selected_estates:
            num_companies = random.randint(2, min(4, len(estate_data['companies'])))
            selected_companies = random.sample(estate_data['companies'], num_companies)
            
            for company in selected_companies:
                if len(facilities) >= self.max_facilities:
                    break
                
                facilities.append({
                    'company_name': company,
                    'industry_type': random.choice(estate_data['industries']),
                    'city': estate_data['city'],
                    'state': estate_data['state'],
                    'industrial_cluster': estate_data['estate'],
                    'data_source': f'Demo: {self.source_name}',
                    'latitude': self._get_coordinates(estate_data['city'])[0],
                    'longitude': self._get_coordinates(estate_data['city'])[1]
                })
        
        return facilities[:self.max_facilities]
    
    def _generate_company_directory_facilities(self) -> List[Dict]:
        """Generate facilities from business directories"""
        directory_companies = [
            {'name': 'Indo-Tech Precision', 'industry': 'Engineering/Machinery', 'city': 'Coimbatore', 'state': 'Tamil Nadu'},
            {'name': 'Global Garments Ltd', 'industry': 'Garment Manufacturing', 'city': 'Tiruppur', 'state': 'Tamil Nadu'},
            {'name': 'Apex Chemicals', 'industry': 'Chemical Plants', 'city': 'Chennai', 'state': 'Tamil Nadu'},
            {'name': 'Precision Auto Parts', 'industry': 'Auto Components', 'city': 'Hosur', 'state': 'Tamil Nadu'},
            {'name': 'Techno Electronics', 'industry': 'Electronics Manufacturing', 'city': 'Bangalore', 'state': 'Karnataka'},
            {'name': 'Prime Steel Industries', 'industry': 'Steel/Metal Processing', 'city': 'Salem', 'state': 'Tamil Nadu'},
            {'name': 'Heritage Textiles', 'industry': 'Textile Manufacturing', 'city': 'Karur', 'state': 'Tamil Nadu'},
            {'name': 'Modern Plastics', 'industry': 'Plastics Manufacturing', 'city': 'Chennai', 'state': 'Tamil Nadu'},
            {'name': 'United Pharma', 'industry': 'Pharmaceutical Manufacturing', 'city': 'Bangalore', 'state': 'Karnataka'},
            {'name': 'Supreme Packaging', 'industry': 'Packaging', 'city': 'Coimbatore', 'state': 'Tamil Nadu'},
        ]
        
        num_facilities = min(self.max_facilities, len(directory_companies))
        selected_companies = random.sample(directory_companies, num_facilities)
        
        facilities = []
        for company in selected_companies:
            cluster = self.extract_cluster_name(company['city'], company['city'])
            facilities.append({
                'company_name': company['name'],
                'industry_type': company['industry'],
                'city': company['city'],
                'state': company['state'],
                'industrial_cluster': cluster,
                'data_source': f'Demo: {self.source_name}',
                'latitude': self._get_coordinates(company['city'])[0],
                'longitude': self._get_coordinates(company['city'])[1]
            })
        
        return facilities
    
    def _get_coordinates(self, city: str) -> tuple:
        """Get approximate coordinates for cities"""
        coordinates = {
            'Tiruppur': (11.1075, 77.3398),
            'Coimbatore': (11.0168, 76.9558),
            'Sriperumbudur': (12.9713, 79.9445),
            'Hosur': (12.7409, 77.8253),
            'Bangalore': (13.0317, 77.5199),
            'Chennai': (13.0827, 80.2707),
            'Salem': (11.6643, 78.1460),
            'Erode': (11.3410, 77.7172),
            'Karur': (10.9601, 78.0766),
            'Madurai': (9.9252, 78.1198),
            'Vellore': (12.9165, 79.1325)
        }
        return coordinates.get(city, (12.9716, 77.5946))

# Demo source configurations
DEMO_SOURCES = [
    {
        'name': 'District Industries Centre - Tamil Nadu',
        'type': 'cluster_directory',
        'max_facilities': 8
    },
    {
        'name': 'SIPCOT Industrial Parks',
        'type': 'estate_listing',
        'max_facilities': 6
    },
    {
        'name': 'IndiaMART Manufacturing Directory',
        'type': 'company_directory',
        'max_facilities': 7
    },
    {
        'name': 'Tiruppur Exporters Association',
        'type': 'cluster_directory',
        'max_facilities': 5
    },
    {
        'name': 'KIADB Industrial Estates',
        'type': 'estate_listing',
        'max_facilities': 5
    }
]
