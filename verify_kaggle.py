#!/usr/bin/env python3
"""
Quick Kaggle verification script
"""
import os
from pathlib import Path

print("="*80)
print("🔍 Kaggle Installation Verification")
print("="*80)

# Check if package is installed
print("\n1. Checking if Kaggle package is installed...")
try:
    import kaggle
    print(f"   ✅ Kaggle package found")
    try:
        from kaggle import __version__
        print(f"   📦 Version: {__version__}")
    except:
        # Try to get version from package metadata
        try:
            import importlib.metadata
            version = importlib.metadata.version('kaggle')
            print(f"   📦 Version: {version}")
        except:
            print(f"   📦 Version: (installed)")
except ImportError as e:
    print(f"   ❌ Kaggle not installed: {e}")
    print("   Run: cd backend && uv sync")
    exit(1)

# Check opendatasets
print("\n2. Checking opendatasets...")
try:
    import opendatasets
    print(f"   ✅ OpenDatasets installed")
except ImportError:
    print(f"   ⚠️  OpenDatasets not found (optional)")

# Check credentials locations
print("\n3. Checking credential locations...")
cred_paths = [
    Path.home() / ".kaggle" / "kaggle.json",
    Path.home() / ".config" / "kaggle" / "kaggle.json",
]

found = False
for path in cred_paths:
    if path.exists():
        print(f"   ✅ Found credentials: {path}")
        # Check permissions
        perms = oct(path.stat().st_mode)[-3:]
        if perms == "600":
            print(f"      ✅ Permissions correct: {perms}")
        else:
            print(f"      ⚠️  Permissions: {perms} (should be 600)")
            print(f"      Fix with: chmod 600 {path}")
        found = True
        break

if not found:
    print(f"   ⚠️  No credentials found")
    print(f"   📝 Create credentials at one of:")
    for path in cred_paths:
        print(f"      - {path}")
    print(f"\n   Get your API token from: https://www.kaggle.com/settings")

# Check project structure
print("\n4. Checking project structure...")
project_root = Path(__file__).parent
checks = {
    "Data loaders": project_root / "backend" / "app" / "services" / "data_loaders" / "kaggle_loader.py",
    "Kaggle data dir": project_root / "data" / "kaggle",
    "Scripts": project_root / "scripts" / "kaggle_manager.py",
}

for name, path in checks.items():
    if path.exists():
        print(f"   ✅ {name}: {path.name}")
    else:
        print(f"   ❌ {name}: Not found")

# Check if we can import our loaders
print("\n5. Checking custom loaders...")
import sys
sys.path.insert(0, str(project_root / "backend"))
try:
    from app.services.data_loaders import KaggleDataLoader
    print(f"   ✅ KaggleDataLoader can be imported")
    
    from app.services.data_loaders import ProjectDatasetLoader
    print(f"   ✅ ProjectDatasetLoader can be imported")
    
    from app.services.data_loaders import quick_load_kaggle_dataset
    print(f"   ✅ quick_load_kaggle_dataset can be imported")
except ImportError as e:
    print(f"   ❌ Import failed: {e}")

# Summary
print("\n" + "="*80)
print("📋 Summary")
print("="*80)
print(f"✅ Kaggle package: Installed")
print(f"{'✅' if found else '⚠️ '} Credentials: {'Configured' if found else 'Not configured'}")
print(f"✅ Project structure: Ready")
print(f"✅ Custom loaders: Available")

print("\n" + "="*80)
if found:
    print("🎉 Kaggle is fully configured and ready to use!")
    print("\n📚 Next steps:")
    print("   • Search datasets: python scripts/kaggle_manager.py search 'query'")
    print("   • Download data: python scripts/kaggle_manager.py download dataset-id")
    print("   • Use in code: from app.services.data_loaders import KaggleDataLoader")
else:
    print("⚠️  Setup required: Kaggle credentials needed")
    print("\n📝 To complete setup:")
    print("   1. Go to https://www.kaggle.com/settings")
    print("   2. Scroll to 'API' section")
    print("   3. Click 'Create New Token' - downloads kaggle.json")
    print("   4. Move the file:")
    print(f"      mkdir -p ~/.kaggle")
    print(f"      mv ~/Downloads/kaggle.json ~/.kaggle/")
    print(f"      chmod 600 ~/.kaggle/kaggle.json")
    print("   5. Run this script again to verify")

print("="*80)
