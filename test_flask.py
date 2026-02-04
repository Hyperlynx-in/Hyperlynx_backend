"""
Simple test to verify Flask application works
"""
import sys
import os

# Ensure imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set environment to suppress database connection attempts for this test
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

from application import app

def test_app():
    """Test that Flask app is created"""
    assert app is not None
    print("✓ Flask app created successfully")
    
def test_health_endpoint():
    """Test health check endpoint"""
    with app.test_client() as client:
        response = client.get('/api/health')
        print(f"  Health status code: {response.status_code}")
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert data['message'] == 'Hyperlynx API is running'
        print("✓ Health endpoint working")

def test_framework_library_endpoint():
    """Test framework library listing endpoint"""
    with app.test_client() as client:
        response = client.get('/api/framework-library')
        print(f"  Framework library status code: {response.status_code}")
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'count' in data
        assert 'data' in data
        print(f"✓ Framework library endpoint working ({data['count']} frameworks found)")

if __name__ == '__main__':
    print("Testing Flask application...\n")
    test_app()
    test_health_endpoint()
    test_framework_library_endpoint()
    print("\n✅ All tests passed!")
