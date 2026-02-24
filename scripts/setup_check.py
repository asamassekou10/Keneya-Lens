"""
Pre-flight setup verification script
Checks if everything is ready to run MedLens
"""
import sys
import subprocess
from pathlib import Path
import importlib.util

def check_python_version():
    """Check Python version."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required. Current:", sys.version)
        return False
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def check_dependencies():
    """Check if required packages are installed."""
    required_packages = [
        'torch',
        'transformers',
        'sentence_transformers',
        'chromadb',
        'fastapi',
        'streamlit',
        'pdfplumber',
        'PIL'
    ]
    
    missing = []
    for package in required_packages:
        try:
            if package == 'PIL':
                __import__('PIL')
            else:
                __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("   Run: pip install -r requirements.txt")
        return False
    return True

def check_directories():
    """Check if required directories exist or can be created."""
    dirs = ['data', 'data/chroma_db', 'data/uploads', 'data/logs', 'models']
    all_ok = True
    
    for dir_path in dirs:
        path = Path(dir_path)
        try:
            path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Directory: {dir_path}")
        except Exception as e:
            print(f"❌ Directory {dir_path}: {e}")
            all_ok = False
    
    return all_ok

def check_files():
    """Check if required files exist."""
    required_files = [
        'app/medgemma_engine.py',
        'app/api.py',
        'app/streamlit_app.py',
        'utils/pdf_processor.py',
        'requirements.txt'
    ]
    
    all_ok = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ File: {file_path}")
        else:
            print(f"❌ File missing: {file_path}")
            all_ok = False
    
    return all_ok

def check_ports():
    """Check if ports are available."""
    import socket
    
    ports = [8000, 8501]
    all_ok = True
    
    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result == 0:
            print(f"⚠️  Port {port} is already in use")
            print(f"   You may need to stop the service using this port")
        else:
            print(f"✅ Port {port} is available")
    
    return True  # Not blocking, just warning

def check_disk_space():
    """Check available disk space."""
    import shutil
    
    try:
        total, used, free = shutil.disk_usage(".")
        free_gb = free / (1024**3)
        
        if free_gb < 10:
            print(f"⚠️  Low disk space: {free_gb:.2f}GB free (10GB+ recommended)")
            return False
        else:
            print(f"✅ Disk space: {free_gb:.2f}GB free")
            return True
    except Exception as e:
        print(f"⚠️  Could not check disk space: {e}")
        return True  # Don't block on this

def main():
    """Run all checks."""
    print("=" * 60)
    print("MedLens Setup Verification")
    print("=" * 60)
    print()
    
    checks = [
        ("Python Version", check_python_version),
        ("Required Files", check_files),
        ("Dependencies", check_dependencies),
        ("Directories", check_directories),
        ("Port Availability", check_ports),
        ("Disk Space", check_disk_space),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n[{name}]")
        print("-" * 40)
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Check failed: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    all_passed = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
        if not result:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 All checks passed! You're ready to run MedLens.")
        print("\nNext steps:")
        print("1. Start backend: python run_api.py")
        print("2. Start frontend: python run_streamlit.py")
        print("3. Open browser: http://localhost:8501")
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
