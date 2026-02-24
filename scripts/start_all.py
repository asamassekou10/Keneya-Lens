"""
Convenience script to start both backend and frontend
Works on Windows, Linux, and Mac
"""
import subprocess
import sys
import time
import os
from pathlib import Path

def start_backend():
    """Start the FastAPI backend."""
    print("🚀 Starting FastAPI backend...")
    if sys.platform == "win32":
        return subprocess.Popen(
            [sys.executable, "run_api.py"],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    else:
        return subprocess.Popen(
            [sys.executable, "run_api.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

def start_frontend():
    """Start the Streamlit frontend."""
    print("🚀 Starting Streamlit frontend...")
    time.sleep(3)  # Wait for backend to start
    
    import os
    address = os.getenv("STREAMLIT_ADDRESS", "localhost")
    port = os.getenv("STREAMLIT_PORT", "8501")
    
    if sys.platform == "win32":
        return subprocess.Popen(
            [
                sys.executable, "-m", "streamlit", "run", "app/streamlit_app.py",
                f"--server.port={port}",
                f"--server.address={address}"
            ],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    else:
        return subprocess.Popen(
            [
                sys.executable, "-m", "streamlit", "run", "app/streamlit_app.py",
                f"--server.port={port}",
                f"--server.address={address}"
            ]
        )

def main():
    """Start both services."""
    print("=" * 60)
    print("MedLens - Starting Services")
    print("=" * 60)
    print()
    
    # Change to project directory
    script_dir = Path(__file__).parent.parent
    os.chdir(script_dir)
    
    try:
        backend = start_backend()
        print(f"✅ Backend started (PID: {backend.pid})")
        
        frontend = start_frontend()
        print(f"✅ Frontend started (PID: {frontend.pid})")
        
        print()
        print("=" * 60)
        print("Services Running")
        print("=" * 60)
        print("Backend:  http://localhost:8000")
        print("Frontend: http://localhost:8501")
        print()
        print("Press Ctrl+C to stop all services")
        print("=" * 60)
        
        # Wait for user interrupt
        try:
            backend.wait()
            frontend.wait()
        except KeyboardInterrupt:
            print("\n\nStopping services...")
            backend.terminate()
            frontend.terminate()
            print("✅ Services stopped")
            
    except Exception as e:
        print(f"❌ Error starting services: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
