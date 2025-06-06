set -e

# Setup venv 
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi

# Activate and install
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Run pipeline
python run_pipeline.py
