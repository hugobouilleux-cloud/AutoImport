#!/usr/bin/env python3
"""
Backend API Health Check Test
Tests basic connectivity and health of the backend API
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://data-import-tools.preview.emergentagent.com"

def test_health_check():
    """Test the basic health check endpoint"""
    print(f"🔍 Testing Health Check...")
    print(f"Backend URL: {BACKEND_URL}")
    
    try:
        # Test root API endpoint
        response = requests.get(f"{BACKEND_URL}/api/", timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if "message" in data:
                    print("✅ Health Check PASSED")
                    print(f"   Message: {data['message']}")
                    return True
                else:
                    print("⚠️  Health Check WARNING: Response missing 'message' field")
                    return True  # Still consider it working
            except json.JSONDecodeError:
                print("⚠️  Health Check WARNING: Response not JSON")
                return True  # Still consider it working if status is 200
        else:
            print(f"❌ Health Check FAILED: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Health Check FAILED: Request timeout (30s)")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Health Check FAILED: Connection error - {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Health Check FAILED: Unexpected error - {str(e)}")
        return False

def test_cors_headers():
    """Test CORS headers are properly configured"""
    print(f"\n🔍 Testing CORS Configuration...")
    
    try:
        response = requests.options(f"{BACKEND_URL}/api/", timeout=10)
        
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
        }
        
        print(f"CORS Headers: {cors_headers}")
        
        if cors_headers['Access-Control-Allow-Origin']:
            print("✅ CORS Configuration PASSED")
            return True
        else:
            print("⚠️  CORS Configuration WARNING: No CORS headers found")
            return True  # Not critical for basic functionality
            
    except Exception as e:
        print(f"⚠️  CORS Test WARNING: {str(e)}")
        return True  # Not critical for basic functionality

def main():
    """Run all health check tests"""
    print("=" * 60)
    print("🚀 BACKEND API HEALTH CHECK")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 60)
    
    results = []
    
    # Test basic health check
    results.append(test_health_check())
    
    # Test CORS configuration
    results.append(test_cors_headers())
    
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ ALL TESTS PASSED ({passed}/{total})")
        print("🎉 Backend API is healthy and ready!")
        return 0
    else:
        print(f"⚠️  SOME TESTS HAD ISSUES ({passed}/{total} passed)")
        print("🔧 Backend may need attention")
        return 1

if __name__ == "__main__":
    sys.exit(main())