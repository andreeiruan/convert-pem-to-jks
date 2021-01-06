# Create venv
python -m venv env
source env/scripts/activate

# Install dependencies
cd chilkat && python installChilkat.py && cd ../
pip install -r requirements.txt

# Build observer
pyinstaller --onefile --noconsole index.py

# Build script
pyinstaller --onefile --noconsole toJks.py