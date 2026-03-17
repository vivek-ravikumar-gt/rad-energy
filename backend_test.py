#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime
from typing import Dict, Any

class RADBackendTester:
    def __init__(self, base_url="https://rad-energy.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        self.passed_tests = []

    def run_test(self, name: str, method: str, endpoint: str, expected_status: int, 
                 data: Dict[Any, Any] = None, validate_response: callable = None) -> tuple:
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)
            elif method == 'PATCH':
                response = requests.patch(url, json=data, headers=headers, timeout=10)

            success = response.status_code == expected_status
            
            if success:
                response_data = {}
                try:
                    response_data = response.json() if response.text else {}
                except:
                    response_data = {}
                
                # Run additional validation if provided
                if validate_response:
                    validation_result = validate_response(response_data)
                    if not validation_result:
                        success = False
                        print(f"❌ Failed validation for {name}")
                
                if success:
                    self.tests_passed += 1
                    self.passed_tests.append(name)
                    print(f"✅ Passed - Status: {response.status_code}")
                    if response_data:
                        print(f"   Response preview: {str(response_data)[:200]}...")
                
                return success, response_data
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                self.failed_tests.append({
                    "name": name,
                    "expected": expected_status,
                    "actual": response.status_code,
                    "response": response.text[:200]
                })
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.failed_tests.append({
                "name": name,
                "error": str(e)
            })
            return False, {}

    def validate_dashboard_stats(self, data):
        """Validate dashboard stats response structure"""
        required_fields = ['total_facilities', 'total_solar_potential_kw', 
                          'total_power_demand_mw', 'avg_opportunity_score', 'facilities_with_renewable']
        for field in required_fields:
            if field not in data:
                print(f"Missing required field: {field}")
                return False
        return data['total_facilities'] >= 0

    def validate_facilities_list(self, data):
        """Validate facilities list response"""
        if not isinstance(data, list):
            print("Expected list of facilities")
            return False
        
        if len(data) > 0:
            facility = data[0]
            required_fields = ['id', 'company_name', 'industry_type', 'city', 
                             'renewable_opportunity_score', 'estimated_solar_capacity_kw']
            for field in required_fields:
                if field not in facility:
                    print(f"Missing required facility field: {field}")
                    return False
        return True

    def validate_single_facility(self, data):
        """Validate single facility response"""
        required_fields = ['id', 'company_name', 'industry_type', 'city', 'state',
                          'renewable_opportunity_score', 'estimated_solar_capacity_kw', 
                          'estimated_power_demand_mw']
        for field in required_fields:
            if field not in data:
                print(f"Missing required facility field: {field}")
                return False
        return True

    def validate_clusters(self, data):
        """Validate clusters response"""
        if not isinstance(data, list):
            print("Expected list of clusters")
            return False
            
        if len(data) > 0:
            cluster = data[0]
            required_fields = ['cluster_name', 'city', 'company_count', 
                             'total_power_demand_mw', 'total_solar_potential_kw']
            for field in required_fields:
                if field not in cluster:
                    print(f"Missing required cluster field: {field}")
                    return False
        return True

    def validate_email_generation(self, data):
        """Validate email generation response"""
        required_fields = ['email_content', 'facility_name']
        for field in required_fields:
            if field not in data:
                print(f"Missing required email field: {field}")
                return False
        return len(data['email_content']) > 50  # Should be substantial content

    def test_backend_apis(self):
        """Test all backend API endpoints"""
        print("🚀 Starting RAD Backend API Testing...")
        print(f"Testing against: {self.api_url}")
        
        # Test 1: Root API endpoint
        self.run_test("API Root", "GET", "", 200)
        
        # Test 2: Dashboard stats
        self.run_test("Dashboard Stats", "GET", "dashboard/stats", 200, 
                     validate_response=self.validate_dashboard_stats)
        
        # Test 3: Get all facilities
        success, facilities_data = self.run_test("Get All Facilities", "GET", "facilities", 200,
                                                 validate_response=self.validate_facilities_list)
        
        # Test 4: Get facilities with city filter
        self.run_test("Filter Facilities by City", "GET", "facilities?city=Chennai", 200)
        
        # Test 5: Get facilities with industry filter  
        self.run_test("Filter Facilities by Industry", "GET", "facilities?industry_type=Electronics", 200)
        
        # Test 6: Get facilities with score filter
        self.run_test("Filter Facilities by Score", "GET", "facilities?min_score=80", 200)
        
        # Test 7: Get top prospects
        success, prospects_data = self.run_test("Top Prospects", "GET", "facilities/top/prospects?limit=10", 200,
                                               validate_response=self.validate_facilities_list)
        
        # Test 8: Get single facility (if we have facilities)
        if success and facilities_data and len(facilities_data) > 0:
            facility_id = facilities_data[0]['id']
            self.run_test("Get Single Facility", "GET", f"facilities/{facility_id}", 200,
                         validate_response=self.validate_single_facility)
            
            # Test 9: Email generation for this facility
            self.run_test("Generate Email", "POST", "email/generate", 200,
                         data={"facility_id": facility_id},
                         validate_response=self.validate_email_generation)
        else:
            print("⚠️  Skipping facility-specific tests - no facilities found")
        
        # Test 10: Get cluster statistics
        self.run_test("Cluster Statistics", "GET", "clusters", 200,
                     validate_response=self.validate_clusters)
        
        # Test 11: Error handling - non-existent facility
        self.run_test("Non-existent Facility (404)", "GET", "facilities/non-existent-id", 404)

    def print_summary(self):
        """Print test results summary"""
        print(f"\n📊 TEST SUMMARY")
        print(f"Tests run: {self.tests_run}")
        print(f"Tests passed: {self.tests_passed}")
        print(f"Tests failed: {len(self.failed_tests)}")
        print(f"Success rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.failed_tests:
            print(f"\n❌ FAILED TESTS:")
            for test in self.failed_tests:
                print(f"  - {test['name']}")
                if 'error' in test:
                    print(f"    Error: {test['error']}")
                else:
                    print(f"    Expected: {test['expected']}, Got: {test['actual']}")

        if self.passed_tests:
            print(f"\n✅ PASSED TESTS:")
            for test in self.passed_tests:
                print(f"  - {test}")
        
        return len(self.failed_tests) == 0

def main():
    """Main test execution"""
    tester = RADBackendTester()
    tester.test_backend_apis()
    success = tester.print_summary()
    
    # Return appropriate exit code
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())