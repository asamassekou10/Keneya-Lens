"""
Compatibility check for PyTorch and transformers
Run this before importing transformers to catch issues early
"""
import sys

def check_pytorch_compatibility():
    """Check if PyTorch version is compatible."""
    try:
        import torch
        version = torch.__version__
        major, minor = map(int, version.split('.')[:2])
        
        if major < 2 or (major == 2 and minor < 1):
            print(f"⚠️  Warning: PyTorch {version} may not be compatible.")
            print("   Recommended: PyTorch 2.1.0 or higher")
            print("   Run: pip install --upgrade torch>=2.1.0")
            return False
        
        # Check for pytree support
        try:
            from torch.utils import _pytree
            if not hasattr(_pytree, 'register_pytree_node'):
                print("⚠️  Warning: PyTorch pytree module missing required function")
                print("   This may cause compatibility issues with transformers")
                print("   Run: pip install --upgrade torch>=2.1.0")
                return False
        except ImportError:
            print("⚠️  Warning: PyTorch pytree module not available")
            print("   Run: pip install --upgrade torch>=2.1.0")
            return False
        
        return True
        
    except ImportError:
        print("❌ PyTorch not installed")
        print("   Run: pip install torch>=2.1.0")
        return False

def check_transformers_compatibility():
    """Check if transformers can be imported."""
    try:
        import transformers
        return True
    except AttributeError as e:
        if 'register_pytree_node' in str(e):
            print("❌ Compatibility error detected!")
            print("   PyTorch and transformers versions are incompatible")
            print("   Run: python scripts/fix_dependencies.py")
            return False
        raise
    except ImportError:
        print("❌ Transformers not installed")
        print("   Run: pip install transformers>=4.35.0")
        return False

def run_compatibility_check():
    """Run all compatibility checks."""
    print("Checking compatibility...")
    
    pytorch_ok = check_pytorch_compatibility()
    if not pytorch_ok:
        return False
    
    transformers_ok = check_transformers_compatibility()
    if not transformers_ok:
        return False
    
    print("✅ Compatibility check passed!")
    return True

if __name__ == "__main__":
    success = run_compatibility_check()
    sys.exit(0 if success else 1)
