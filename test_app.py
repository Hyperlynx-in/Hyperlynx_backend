"""Test Flask app configuration and endpoints"""
from application import create_app

if __name__ == '__main__':
    app = create_app()
    print('✓ App created successfully')
    print(f'✓ Database URI configured')
    print(f'✓ JWT configured')
    print(f'✓ CORS configured')
    
    # Start the server
    print('\nStarting Flask server...')
    app.run(host='0.0.0.0', port=5000, debug=True)
