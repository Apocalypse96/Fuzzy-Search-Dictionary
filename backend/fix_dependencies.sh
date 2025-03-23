#!/bin/bash

echo "Activating virtual environment..."
source venv/bin/activate || { echo "Failed to activate venv. Is it created?"; exit 1; }

echo "Uninstalling potentially conflicting packages..."
pip uninstall -y bcrypt passlib

echo "Installing dependencies with specific versions..."
pip install -r requirements.txt

echo "Testing bcrypt functionality..."
python -c "import bcrypt; print('bcrypt version:', bcrypt.__version__); \
           print('Test hash:', bcrypt.hashpw('test'.encode(), bcrypt.gensalt()).decode())"

echo "==================================="
echo "Setup complete! To run the application:"
echo "1. Make sure the virtual environment is activated:"
echo "   source venv/bin/activate"
echo ""
echo "2. Run the FastAPI application:"
echo "   uvicorn main:app --reload"
echo "==================================="
