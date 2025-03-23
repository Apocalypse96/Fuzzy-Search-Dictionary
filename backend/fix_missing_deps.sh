#!/bin/bash

echo "Installing missing dependencies..."

# Check if virtual environment exists
if [ -d "venv" ]; then
  echo "Activating virtual environment..."
  source venv/bin/activate || { echo "Failed to activate virtual environment"; exit 1; }
else
  echo "Creating new virtual environment..."
  python3 -m venv venv || { echo "Failed to create virtual environment"; exit 1; }
  source venv/bin/activate || { echo "Failed to activate virtual environment"; exit 1; }
fi

# Install dependencies
echo "Installing required packages from requirements.txt..."
pip install -r requirements.txt

echo "Verifying python-dotenv installation..."
python -c "import dotenv; print('python-dotenv successfully installed')" || {
  echo "Direct installation of python-dotenv..."
  pip install python-dotenv
}

echo "Done! You can now run the backend server with: uvicorn main:app --reload"
