"""
Fix dependency compatibility issues
Run this if you encounter PyTorch/transformers compatibility errors
"""
import subprocess
import sys

def fix_dependencies():
    """Fix PyTorch and transformers compatibility."""
    print("=" * 60)
    print("Fixing Dependency Compatibility Issues")
    print("=" * 60)
    print()
    
    print("Step 1: Uninstalling conflicting packages...")
    packages_to_remove = ['torch', 'transformers', 'accelerate']
    for package in packages_to_remove:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "uninstall", package, "-y"])
            print(f"✅ Uninstalled {package}")
        except:
            print(f"⚠️  Could not uninstall {package} (may not be installed)")
    
    print()
    print("Step 2: Installing compatible versions...")
    
    # Install PyTorch first (CPU version for compatibility)
    print("\nInstalling PyTorch...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install",
            "torch>=2.1.0,<2.5.0",
            "--index-url", "https://download.pytorch.org/whl/cpu"
        ])
        print("✅ PyTorch installed")
    except Exception as e:
        print(f"⚠️  PyTorch CPU install failed: {e}")
        print("Trying default PyTorch...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "torch>=2.1.0,<2.5.0"
        ])
    
    # Install transformers
    print("\nInstalling transformers...")
    subprocess.check_call([
        sys.executable, "-m", "pip", "install",
        "transformers>=4.35.0,<5.0.0"
    ])
    print("✅ Transformers installed")
    
    # Install accelerate
    print("\nInstalling accelerate...")
    subprocess.check_call([
        sys.executable, "-m", "pip", "install", "accelerate>=0.24.0"
    ])
    print("✅ Accelerate installed")
    
    print()
    print("=" * 60)
    print("✅ Dependency fix complete!")
    print("=" * 60)
    print()
    print("Please restart your backend server:")
    print("  python run_api.py")
    print()

if __name__ == "__main__":
    try:
        fix_dependencies()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nManual fix:")
        print("1. pip uninstall torch transformers accelerate -y")
        print("2. pip install torch>=2.1.0,<2.5.0")
        print("3. pip install transformers>=4.35.0,<5.0.0")
        print("4. pip install accelerate>=0.24.0")
        sys.exit(1)
