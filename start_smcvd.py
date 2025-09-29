#!/usr/bin/env python3
"""
Enhanced startup script for SMCVD with dependency checking and installation
"""
import sys
import subprocess
import os
from pathlib import Path

def check_python_version():
    """Ensure Python version is compatible"""
    if sys.version_info < (3, 9):
        print("❌ Python 3.9+ is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_requirements():
    """Install required packages"""
    requirements_file = Path("requirements.txt")
    
    if not requirements_file.exists():
        print("❌ requirements.txt not found")
        return False
    
    print("📦 Installing/updating dependencies...")
    try:
        # Upgrade pip first
        subprocess.run([
            sys.executable, "-m", "pip", "install", "--upgrade", "pip"
        ], check=True, capture_output=True)
        
        # Install requirements
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True, capture_output=True, text=True)
        
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_env_setup():
    """Check and suggest environment variable setup"""
    print("\n🔧 Environment Configuration:")
    
    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  OPENAI_API_KEY not set (AI features will be disabled)")
        print("   To enable AI: set OPENAI_API_KEY=your_api_key_here")
    else:
        print("✅ OPENAI_API_KEY is set")
    
    # Check other important env vars
    env_vars = {
        'MIN_CONFIDENCE': '0.65',
        'ENABLE_AI': 'true',
        'SECRET_KEY': 'your-secret-key-here'
    }
    
    for var, default in env_vars.items():
        value = os.getenv(var)
        if not value:
            print(f"⚠️  {var} not set (using default: {default})")
        else:
            masked_value = value if var != 'SECRET_KEY' else '***'
            print(f"✅ {var} = {masked_value}")

def run_import_test():
    """Run the import test"""
    print("\n🧪 Testing imports...")
    try:
        result = subprocess.run([
            sys.executable, "test_imports.py"
        ], capture_output=True, text=True)
        
        if "All imports working correctly!" in result.stdout:
            print("✅ All imports working!")
            return True
        else:
            print("⚠️  Some imports need dependencies, but app will run with fallbacks")
            print("Install missing packages with: pip install flask flask-cors openai")
            return True  # Still can run with fallbacks
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def start_application():
    """Start the SMCVD application"""
    print("\n🚀 Starting SMCVD...")
    try:
        # Change to the project directory
        os.chdir(Path(__file__).parent)
        
        # Start the application
        subprocess.run([sys.executable, "src/app.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 SMCVD stopped by user")
    except Exception as e:
        print(f"❌ Failed to start application: {e}")

def main():
    """Main startup routine"""
    print("🔧 SMCVD Enhanced Startup")
    print("=" * 40)
    
    # Step 1: Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Step 2: Install dependencies
    print("\n📋 Checking dependencies...")
    deps_ok = True
    try:
        import flask
        import openai
        print("✅ Core dependencies already installed")
    except ImportError:
        print("⚠️  Some dependencies missing, installing...")
        deps_ok = install_requirements()
    
    if not deps_ok:
        print("\n❌ Could not install dependencies. Try manually:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    
    # Step 3: Check environment setup
    check_env_setup()
    
    # Step 4: Test imports
    if not run_import_test():
        print("\n❌ Critical import issues detected")
        sys.exit(1)
    
    # Step 5: Start application
    print("\n" + "=" * 40)
    start_application()

if __name__ == "__main__":
    main()
