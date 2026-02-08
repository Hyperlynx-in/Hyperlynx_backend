"""Test library API endpoints"""
from application import create_app
import json

app = create_app()

with app.test_client() as client:
    print("Testing Library Management API Endpoints\n")
    
    # Test 1: List stored libraries
    print("1. GET /api/stored-libraries/ (limit=5)")
    response = client.get('/api/stored-libraries/?limit=5')
    data = response.get_json()
    print(f"   Status: {response.status_code}")
    print(f"   Total libraries: {data.get('count')}")
    print(f"   Returned: {len(data.get('results', []))}")
    if data.get('results'):
        print(f"   First library: {data['results'][0]['name']}")
    
    # Test 2: Search libraries
    print("\n2. GET /api/stored-libraries/?search=iso27001")
    response = client.get('/api/stored-libraries/?search=iso27001')
    data = response.get_json()
    print(f"   Status: {response.status_code}")
    print(f"   Found: {data.get('count')} libraries")
    for lib in data.get('results', [])[:3]:
        print(f"   - {lib['name']}")
    
    # Test 3: Get library providers
    print("\n3. GET /api/stored-libraries/provider/")
    response = client.get('/api/stored-libraries/provider/')
    data = response.get_json()
    print(f"   Status: {response.status_code}")
    print(f"   Providers: {', '.join(data.get('providers', [])[:10])}")
    
    # Test 4: Filter by provider
    print("\n4. GET /api/stored-libraries/?provider=NIST")
    response = client.get('/api/stored-libraries/?provider=NIST')
    data = response.get_json()
    print(f"   Status: {response.status_code}")
    print(f"   NIST libraries: {data.get('count')}")
    
    # Test 5: Get specific library
    print("\n5. GET /api/stored-libraries/urn:intuitem:risk:library:iso27001-2022/")
    response = client.get('/api/stored-libraries/urn:intuitem:risk:library:iso27001-2022/')
    if response.status_code == 200:
        data = response.get_json()
        print(f"   Status: {response.status_code}")
        print(f"   Name: {data.get('name')}")
        print(f"   Version: {data.get('version')}")
        print(f"   Provider: {data.get('provider')}")
    else:
        print(f"   Status: {response.status_code} (library might not exist)")
    
    # Test 6: Get library content
    print("\n6. GET /api/stored-libraries/urn:intuitem:risk:library:nist-csf-2.0/content/")
    response = client.get('/api/stored-libraries/urn:intuitem:risk:library:nist-csf-2.0/content/')
    if response.status_code == 200:
        data = response.get_json()
        print(f"   Status: {response.status_code}")
        print(f"   Has content: {bool(data.get('content'))}")
        if data.get('content', {}).get('objects'):
            objects = data['content']['objects']
            print(f"   Objects: {', '.join(objects.keys())}")
    else:
        print(f"   Status: {response.status_code}")
    
    # Test 7: Import library (load it)
    print("\n7. POST /api/stored-libraries/urn:intuitem:risk:library:nist-csf-2.0/import/")
    response = client.post('/api/stored-libraries/urn:intuitem:risk:library:nist-csf-2.0/import/')
    data = response.get_json()
    print(f"   Status: {response.status_code}")
    print(f"   Message: {data.get('message') or data.get('error')}")
    
    # Test 8: List loaded libraries
    print("\n8. GET /api/loaded-libraries/")
    response = client.get('/api/loaded-libraries/')
    data = response.get_json()
    print(f"   Status: {response.status_code}")
    print(f"   Loaded libraries: {data.get('count')}")
    if data.get('results'):
        for lib in data['results'][:3]:
            print(f"   - {lib['name']}")
    
    # Test 9: List frameworks
    print("\n9. GET /api/frameworks/")
    response = client.get('/api/frameworks/')
    data = response.get_json()
    print(f"   Status: {response.status_code}")
    print(f"   Frameworks: {data.get('count')}")
    if data.get('results'):
        for fw in data['results'][:3]:
            print(f"   - {fw['name']}")
    
    # Test 10: List reference controls
    print("\n10. GET /api/reference-controls/?limit=5")
    response = client.get('/api/reference-controls/?limit=5')
    data = response.get_json()
    print(f"   Status: {response.status_code}")
    print(f"   Controls: {data.get('count')}")
    
    # Test 11: List risk matrices
    print("\n11. GET /api/risk-matrices/")
    response = client.get('/api/risk-matrices/')
    data = response.get_json()
    print(f"   Status: {response.status_code}")
    print(f"   Risk matrices: {data.get('count')}")
    
    # Test 12: Check Swagger UI
    print("\n12. GET /docs (Swagger UI)")
    response = client.get('/docs')
    print(f"   Status: {response.status_code}")
    
    print("\n" + "="*50)
    print("All tests completed!")
