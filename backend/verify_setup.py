#!/usr/bin/env python3
"""
Setup Verification Script
Checks if all components are properly installed and configured
"""
import sys
import importlib
from pathlib import Path

def check_import(module_name, package_name=None):
    """Check if a module can be imported"""
    try:
        importlib.import_module(module_name)
        print(f"✅ {package_name or module_name}")
        return True
    except ImportError as e:
        print(f"❌ {package_name or module_name} - {e}")
        return False

def check_file(file_path, description):
    """Check if a file exists"""
    if Path(file_path).exists():
        print(f"✅ {description}")
        return True
    else:
        print(f"❌ {description} - Not found")
        return False

def main():
    print("=" * 60)
    print("  AI-Powered Risk Early Warning System - Setup Verification")
    print("=" * 60)
    
    print("\n📦 Checking Python Dependencies...")
    dependencies = [
        ("fastapi", "FastAPI"),
        ("sqlmodel", "SQLModel"),
        ("pandas", "pandas"),
        ("numpy", "numpy"),
        ("sklearn", "scikit-learn"),
        ("xgboost", "XGBoost"),
        ("lightgbm", "LightGBM"),
        ("plotly", "Plotly"),
        ("pydantic", "Pydantic"),
        ("uvicorn", "Uvicorn"),
    ]
    
    dep_results = [check_import(mod, name) for mod, name in dependencies]
    
    print("\n📁 Checking Project Structure...")
    files = [
        ("app/main.py", "Main FastAPI application"),
        ("app/core/config.py", "Configuration module"),
        ("app/db/models.py", "Database models"),
        ("app/db/database.py", "Database connection"),
        ("app/ml/risk_models.py", "ML models"),
        ("app/services/data_processing.py", "Data processing"),
        ("app/services/visualization.py", "Visualization"),
        ("app/api/risk_routes.py", "API routes"),
        ("app/services/sample_data_generator.py", "Sample data generator"),
    ]
    
    file_results = [check_file(f, desc) for f, desc in files]
    
    print("\n📊 Checking Data Directories...")
    dirs = [
        ("../data/raw", "Raw data directory"),
        ("../data/processed", "Processed data directory"),
        ("models", "Models directory (will be created)"),
    ]
    
    for dir_path, desc in dirs:
        path = Path(dir_path)
        path.mkdir(parents=True, exist_ok=True)
        check_file(dir_path, desc)
    
    print("\n" + "=" * 60)
    
    # Summary
    total_deps = len(dependencies)
    passed_deps = sum(dep_results)
    total_files = len(files)
    passed_files = sum(file_results)
    
    print(f"\n📊 SUMMARY:")
    print(f"  Dependencies: {passed_deps}/{total_deps} passed")
    print(f"  Project Files: {passed_files}/{total_files} found")
    
    if passed_deps == total_deps and passed_files == total_files:
        print("\n✅ All checks passed! System is ready to use.")
        print("\n🚀 Next steps:")
        print("  1. Copy .env.example to .env and configure")
        print("  2. Generate sample data: python -m app.services.sample_data_generator")
        print("  3. Start server: uvicorn app.main:app --reload")
        print("  4. Open API docs: http://localhost:8000/docs")
        return 0
    else:
        print("\n⚠️  Some checks failed. Please install missing dependencies:")
        print("     cd backend && uv sync")
        print("     or: pip install -e .")
        return 1

if __name__ == "__main__":
    sys.exit(main())
