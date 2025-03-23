#!/bin/bash

echo "Creating Python virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

echo "Downloading NLTK data..."
python download_nltk_data.py

echo "==================================="
echo "Setup complete! To run the application:"
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Run the FastAPI application:"
echo "   uvicorn main:app --reload"
echo "==================================="
