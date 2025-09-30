import os
import subprocess
import sys

# Set environment variables
# Replace 'YOUR_OPENAI_API_KEY_HERE' with your actual OpenAI API key
os.environ['OPENAI_API_KEY'] = 'YOUR_OPENAI_API_KEY_HERE'
os.environ['ENABLE_AI'] = 'true'

# Change to the project directory
os.chdir(r'c:\Users\user23\Downloads\smartcontract')

# Start the service
subprocess.run([sys.executable, 'src/app.py'])