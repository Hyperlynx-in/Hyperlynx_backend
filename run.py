#!/usr/bin/env python
"""
Start the Flask development server
"""
import os
import sys

if __name__ == '__main__':
    from application import app
    
    # Run the Flask development server
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=False,
        use_reloader=False
    )
