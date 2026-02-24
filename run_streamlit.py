"""
Convenience script to run the Streamlit UI
"""
import subprocess
import sys
import os

if __name__ == "__main__":
    # Use localhost for local development, 0.0.0.0 for Docker/remote access
    # Can be overridden with STREAMLIT_ADDRESS environment variable
    address = os.getenv("STREAMLIT_ADDRESS", "localhost")
    port = os.getenv("STREAMLIT_PORT", "8501")
    
    print(f"Starting Streamlit on http://{address}:{port}")
    print("(Use STREAMLIT_ADDRESS=0.0.0.0 for remote access)")
    
    subprocess.run([
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "app/streamlit_app.py",
        f"--server.port={port}",
        f"--server.address={address}"
    ])
