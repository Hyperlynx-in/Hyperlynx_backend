#!/bin/bash
# Linux/Mac script to run Hyperlynx Backend API

echo ""
echo "========================================"
echo "  Hyperlynx Backend API Server"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found!"
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements if needed
echo "Checking dependencies..."
pip install -q -r requirements.txt

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Start server
echo ""
echo "========================================"
echo "   Starting server at http://localhost:8000"
echo "========================================"
echo ""
echo "Press CTRL+C to stop the server"
echo ""
python manage.py runserver

