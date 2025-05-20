#!/bin/bash
# Activate the virtual environment
source venv/bin/activate

# Add the project root to PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Run the API
python3 -m src.api.api
