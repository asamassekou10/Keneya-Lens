"""
Setup HuggingFace authentication for gated models
"""
import os
import sys

def setup_huggingface():
    """Guide user through HuggingFace authentication setup."""
    print("=" * 60)
    print("HuggingFace Authentication Setup")
    print("=" * 60)
    print()
    
    print("The Gemma model requires HuggingFace authentication.")
    print()
    print("Step 1: Get your HuggingFace token")
    print("  1. Visit: https://huggingface.co/settings/tokens")
    print("  2. Click 'New token'")
    print("  3. Name it (e.g., 'medlens-token')")
    print("  4. Select 'Read' permissions")
    print("  5. Copy the token (starts with hf_...)")
    print()
    print("Step 2: Request access to Gemma model")
    print("  1. Visit: https://huggingface.co/google/gemma-2-2b-it")
    print("  2. Click 'Agree and access repository'")
    print("  3. Accept the terms")
    print()
    
    token = input("Enter your HuggingFace token (or press Enter to skip): ").strip()
    
    if not token:
        print("\n⚠️  No token provided. You'll need to set it manually.")
        print("\nTo set it manually:")
        print("  Windows PowerShell: $env:HUGGINGFACE_TOKEN='your_token'")
        print("  Windows CMD: set HUGGINGFACE_TOKEN=your_token")
        print("  Linux/Mac: export HUGGINGFACE_TOKEN='your_token'")
        print("\nOr create a .env file with: HUGGINGFACE_TOKEN=your_token")
        return False
    
    # Verify token format
    if not token.startswith("hf_"):
        print("\n⚠️  Warning: Token should start with 'hf_'")
        proceed = input("Continue anyway? (y/n): ").strip().lower()
        if proceed != 'y':
            return False
    
    # Try to authenticate
    try:
        from huggingface_hub import login, whoami
        login(token=token)
        user_info = whoami()
        print(f"\n✅ Successfully authenticated as: {user_info.get('name', 'Unknown')}")
        
        # Save to .env file
        env_file = ".env"
        env_content = f"HUGGINGFACE_TOKEN={token}\n"
        
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                existing = f.read()
            if "HUGGINGFACE_TOKEN" not in existing:
                with open(env_file, 'a') as f:
                    f.write(env_content)
                print(f"✅ Token saved to {env_file}")
            else:
                print(f"⚠️  {env_file} already contains HUGGINGFACE_TOKEN")
                overwrite = input("Overwrite? (y/n): ").strip().lower()
                if overwrite == 'y':
                    lines = existing.split('\n')
                    lines = [l for l in lines if not l.startswith("HUGGINGFACE_TOKEN")]
                    lines.append(env_content.strip())
                    with open(env_file, 'w') as f:
                        f.write('\n'.join(lines))
                    print(f"✅ Token updated in {env_file}")
        else:
            with open(env_file, 'w') as f:
                f.write(env_content)
            print(f"✅ Token saved to {env_file}")
        
        print("\n✅ Setup complete! You can now run: python run_api.py")
        return True
        
    except ImportError:
        print("\n❌ huggingface_hub not installed")
        print("   Installing...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "huggingface_hub"])
        print("   ✅ Installed. Please run this script again.")
        return False
    except Exception as e:
        print(f"\n❌ Authentication failed: {e}")
        print("\nPlease check:")
        print("  1. Token is correct")
        print("  2. You have access to google/gemma-2-2b-it")
        print("  3. Internet connection is working")
        return False

if __name__ == "__main__":
    success = setup_huggingface()
    sys.exit(0 if success else 1)
