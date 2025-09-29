import sys
import os
import subprocess
import time
import threading

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def start_flask_app():
    """Start the Flask application"""
    try:
        print("Starting SMCVD Flask application...")
        # Change to the project directory
        os.chdir(os.path.join(os.path.dirname(__file__)))
        
        # Start the Flask app
        env = os.environ.copy()
        env['FLASK_APP'] = 'src/app.py'
        env['FLASK_ENV'] = 'development'
        
        # Run the Flask app
        process = subprocess.Popen([
            sys.executable, 
            '-m', 
            'flask', 
            'run', 
            '--host=0.0.0.0', 
            '--port=5000'
        ], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("SMCVD service started successfully!")
        print("Access the service at: http://localhost:5000")
        print("API health check: http://localhost:5000/api/health")
        
        # Print output from the process
        try:
            stdout, stderr = process.communicate(timeout=1)
            if stdout:
                print("STDOUT:", stdout.decode())
            if stderr:
                print("STDERR:", stderr.decode())
        except subprocess.TimeoutExpired:
            # This is expected as the process should continue running
            pass
            
        return process
    except Exception as e:
        print(f"Error starting Flask app: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    print("SMCVD Service Starter")
    print("=" * 20)
    
    process = start_flask_app()
    
    if process:
        print("\nService is running. Press Ctrl+C to stop.")
        try:
            # Wait for the process to complete (it shouldn't in this case)
            process.wait()
        except KeyboardInterrupt:
            print("\nStopping service...")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            print("Service stopped.")

if __name__ == "__main__":
    main()