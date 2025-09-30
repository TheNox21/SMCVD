import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Disable AI features
os.environ['ENABLE_AI'] = 'false'

# Import and run the app
from src.app import create_app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=False)