#!/bin/bash
# Activate the virtual environment
source venv/bin/activate

# Set the PYTHONPATH to include the src directory
export PYTHONPATH=$(pwd)/src

# Run the API
python3 src/webapp/webapp.py
