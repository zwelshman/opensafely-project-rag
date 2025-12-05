#!/bin/bash
# Quick start script for OpenSAFELY Project Search

echo "OpenSAFELY Projects Semantic Search"
echo "===================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "Installing/updating dependencies..."
pip install -q -r requirements.txt

# Generate sample data if no data exists
if [ ! -f "opensafely_projects.json" ]; then
    echo ""
    echo "No project data found. Generating sample data for testing..."
    python sample_data.py
    echo ""
fi

# Run the Streamlit app
echo "Starting Streamlit app..."
echo ""
streamlit run app.py
