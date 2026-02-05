"""Test Flask app directly"""
import os
os.environ['VERCEL'] = '0'  # Force local mode

try:
    from api.index import app
    
    print("✓ App imported from api/index.py")
    print(f"✓ App type: {type(app)}")
    print(f"✓ Routes: {len(list(app.url_map.iter_rules()))}")
    
    # Test with Flask test client
    with app.test_client() as client:
        print("\n=== Testing Endpoints ===")
        
        # Test health
        r = client.get('/api/health')
        print(f"GET /api/health: {r.status_code}")
        print(f"  Response: {r.get_json()}")
        
        # Test frameworks
        r = client.get('/api/framework-library')
        print(f"\nGET /api/framework-library: {r.status_code}")
        data = r.get_json()
        print(f"  Frameworks: {data.get('count', 0)}")
        
        # Test root
        r = client.get('/')
        print(f"\nGET /: {r.status_code}")
        print(f"  Response: {r.get_json()}")
        
        print("\n✓ All endpoints working!")
        
except Exception as e:
    import traceback
    print(f"✗ Error: {e}")
    traceback.print_exc()
