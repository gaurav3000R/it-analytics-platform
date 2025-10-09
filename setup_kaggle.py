#!/usr/bin/env python3
"""
Kaggle Setup and Verification Script
Helps configure Kaggle credentials and verify the installation
"""
import os
import sys
import json
from pathlib import Path

def check_kaggle_installation():
    """Check if Kaggle is installed"""
    try:
        import kaggle
        print(f"✅ Kaggle is installed (version {kaggle.__version__})")
        return True
    except ImportError:
        print("❌ Kaggle is not installed")
        print("   Run: cd backend && uv sync")
        return False

def check_credentials():
    """Check if Kaggle credentials are configured"""
    kaggle_dir = Path.home() / ".kaggle"
    kaggle_json = kaggle_dir / "kaggle.json"
    
    if kaggle_json.exists():
        # Check permissions
        stat_info = kaggle_json.stat()
        perms = oct(stat_info.st_mode)[-3:]
        
        if perms == "600":
            print(f"✅ Kaggle credentials found at {kaggle_json}")
            print(f"✅ Permissions are correct (600)")
            return True
        else:
            print(f"⚠️  Kaggle credentials found but permissions are {perms}")
            print(f"   Run: chmod 600 {kaggle_json}")
            return False
    else:
        print(f"⚠️  Kaggle credentials not found at {kaggle_json}")
        return False

def setup_credentials():
    """Interactive setup for Kaggle credentials"""
    print("\n" + "="*80)
    print("🔧 Kaggle Credentials Setup")
    print("="*80)
    print("\nTo use Kaggle API, you need an API token:")
    print("1. Go to https://www.kaggle.com/settings")
    print("2. Scroll to 'API' section")
    print("3. Click 'Create New Token'")
    print("4. This will download kaggle.json")
    print("\nOptions:")
    print("  A) I have already downloaded kaggle.json")
    print("  B) I will enter my credentials manually")
    print("  C) Skip for now")
    
    choice = input("\nYour choice (A/B/C): ").strip().upper()
    
    kaggle_dir = Path.home() / ".kaggle"
    kaggle_json = kaggle_dir / "kaggle.json"
    
    if choice == 'A':
        downloads_path = Path.home() / "Downloads" / "kaggle.json"
        if downloads_path.exists():
            print(f"\n✅ Found kaggle.json in Downloads")
            kaggle_dir.mkdir(exist_ok=True)
            
            # Copy file
            import shutil
            shutil.copy(downloads_path, kaggle_json)
            kaggle_json.chmod(0o600)
            
            print(f"✅ Moved to {kaggle_json}")
            print(f"✅ Set permissions to 600")
            return True
        else:
            print(f"\n❌ kaggle.json not found in {downloads_path}")
            custom_path = input("Enter the full path to kaggle.json (or press Enter to skip): ").strip()
            
            if custom_path and Path(custom_path).exists():
                import shutil
                kaggle_dir.mkdir(exist_ok=True)
                shutil.copy(custom_path, kaggle_json)
                kaggle_json.chmod(0o600)
                print(f"✅ Copied to {kaggle_json}")
                print(f"✅ Set permissions to 600")
                return True
            else:
                print("⚠️  Skipping setup")
                return False
    
    elif choice == 'B':
        print("\nEnter your Kaggle credentials:")
        username = input("Username: ").strip()
        key = input("API Key: ").strip()
        
        if username and key:
            kaggle_dir.mkdir(exist_ok=True)
            credentials = {
                "username": username,
                "key": key
            }
            
            with open(kaggle_json, 'w') as f:
                json.dump(credentials, f, indent=2)
            
            kaggle_json.chmod(0o600)
            print(f"\n✅ Credentials saved to {kaggle_json}")
            print(f"✅ Set permissions to 600")
            return True
        else:
            print("❌ Invalid credentials")
            return False
    
    else:
        print("\n⚠️  Skipping setup")
        print("   You can set up credentials later by running this script again")
        return False

def test_connection():
    """Test Kaggle API connection"""
    print("\n" + "="*80)
    print("🧪 Testing Kaggle Connection")
    print("="*80)
    
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
        api = KaggleApi()
        api.authenticate()
        
        print("✅ Successfully authenticated with Kaggle API")
        
        # Try a simple search
        print("\n🔍 Testing search functionality...")
        datasets = api.dataset_list(search="test", page_size=3)
        
        if datasets:
            print(f"✅ Search working! Found {len(datasets)} test datasets")
            print("\nSample results:")
            for ds in datasets[:3]:
                print(f"  - {ds.ref}")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        print("\nTroubleshooting:")
        print("  1. Verify your credentials at https://www.kaggle.com/settings")
        print("  2. Check that kaggle.json has correct permissions (600)")
        print("  3. Ensure your API token is not expired")
        return False

def check_project_structure():
    """Verify project structure is correct"""
    print("\n" + "="*80)
    print("📁 Checking Project Structure")
    print("="*80)
    
    project_root = Path(__file__).parent
    checks = [
        ("Backend directory", project_root / "backend"),
        ("Data directory", project_root / "data"),
        ("Kaggle data directory", project_root / "data" / "kaggle"),
        ("Data loaders module", project_root / "backend" / "app" / "services" / "data_loaders"),
        ("Kaggle loader", project_root / "backend" / "app" / "services" / "data_loaders" / "kaggle_loader.py"),
        ("Scripts directory", project_root / "scripts"),
        ("Kaggle manager CLI", project_root / "scripts" / "kaggle_manager.py"),
    ]
    
    all_good = True
    for name, path in checks:
        if path.exists():
            print(f"✅ {name}: {path}")
        else:
            print(f"❌ {name}: {path} (not found)")
            all_good = False
    
    return all_good

def show_usage_examples():
    """Show quick usage examples"""
    print("\n" + "="*80)
    print("💡 Quick Start Examples")
    print("="*80)
    
    print("\n1️⃣  Using the CLI tool:")
    print("   python scripts/kaggle_manager.py search 'project management'")
    print("   python scripts/kaggle_manager.py download username/dataset-name")
    print("   python scripts/kaggle_manager.py list")
    
    print("\n2️⃣  Using Python API:")
    print("""
   from app.services.data_loaders import KaggleDataLoader
   
   loader = KaggleDataLoader()
   datasets = loader.list_datasets("project management")
   df = loader.load_csv_from_dataset("username/dataset", "file.csv")
    """)
    
    print("\n3️⃣  Integration example:")
    print("""
   from app.services.data_loaders import quick_load_kaggle_dataset
   from app.services.data_processing import DataPipeline
   
   # Load data from Kaggle
   df = quick_load_kaggle_dataset("username/dataset", "metrics.csv")
   
   # Process with existing pipeline
   pipeline = DataPipeline()
   processed = pipeline.process_project_data(df)
    """)
    
    print("\n📚 Full documentation: docs/KAGGLE_INTEGRATION.md")

def main():
    """Main setup flow"""
    print("\n" + "="*80)
    print("🚀 Kaggle Setup and Verification for IT Analytics Platform")
    print("="*80)
    
    # Step 1: Check installation
    print("\n[1/4] Checking Kaggle installation...")
    if not check_kaggle_installation():
        print("\n❌ Please install dependencies first:")
        print("   cd backend && uv sync")
        return 1
    
    # Step 2: Check project structure
    print("\n[2/4] Verifying project structure...")
    if not check_project_structure():
        print("\n⚠️  Some project files are missing")
        print("   The project structure may be incomplete")
    
    # Step 3: Check/setup credentials
    print("\n[3/4] Checking credentials...")
    has_credentials = check_credentials()
    
    if not has_credentials:
        setup = input("\nWould you like to set up credentials now? (y/n): ").strip().lower()
        if setup == 'y':
            has_credentials = setup_credentials()
    
    # Step 4: Test connection
    if has_credentials:
        test_connection()
    else:
        print("\n⚠️  Skipping connection test (no credentials)")
        print("   Run this script again when you have your Kaggle API token")
    
    # Show usage examples
    show_usage_examples()
    
    # Summary
    print("\n" + "="*80)
    print("📋 Setup Summary")
    print("="*80)
    print(f"{'✅' if True else '❌'} Kaggle installed")
    print(f"{'✅' if has_credentials else '⚠️ '} Credentials configured")
    print(f"{'✅' if check_project_structure() else '⚠️ '} Project structure verified")
    
    if has_credentials:
        print("\n🎉 Kaggle is ready to use!")
        print("\n📚 Next steps:")
        print("   1. Search for datasets: python scripts/kaggle_manager.py search 'your query'")
        print("   2. Download data: python scripts/kaggle_manager.py download dataset-id")
        print("   3. Start loading data into your pipeline")
    else:
        print("\n⚠️  Setup incomplete - credentials needed")
        print("   Get your API token from: https://www.kaggle.com/settings")
        print("   Then run this script again")
    
    print("\n" + "="*80)
    return 0

if __name__ == "__main__":
    sys.exit(main())
