#!/usr/bin/env python3
"""
Script to generate sample cost data for existing projects
Run this after loading the CSV project data
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import connect_db
from .generate_cost_sample_data import generate_sample_cost_data
import argparse

def main():
    parser = argparse.ArgumentParser(description="Generate sample cost data for projects")
    parser.add_argument(
        "--employees",
        type=int,
        default=50,
        help="Number of employees to create (default: 50)"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=90,
        help="Days of historical data to generate (default: 90)"
    )
    parser.add_argument(
        "--clear-logs",
        action="store_true",
        help="Clear existing daily logs before generating new data"
    )
    parser.add_argument(
        "--clear-employees",
        action="store_true",
        help="Clear existing employees before generating new data"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Cost Forecasting Sample Data Generator")
    print("=" * 60)
    print(f"Employees to create: {args.employees}")
    print(f"Days of history: {args.days}")
    print()
    
    # Connect to database
    print("Connecting to Supabase...")
    db = connect_db()
    
    if not db:
        print("❌ Failed to connect to database")
        print("Please check your SUPABASE_URL and SUPABASE_KEY in .env")
        return 1
    
    print("✅ Connected to Supabase")
    
    # Clear existing data if requested
    if args.clear_employees:
        print("\n🗑️  Clearing existing employees...")
        try:
            db.table('employees').delete().neq('id', 0).execute()
            print("✅ Employees cleared")
        except Exception as e:
            print(f"⚠️  Warning: Could not clear employees: {e}")
    
    if args.clear_logs:
        print("\n🗑️  Clearing existing daily logs...")
        try:
            db.table('daily_logs').delete().neq('id', 0).execute()
            print("✅ Daily logs cleared")
        except Exception as e:
            print(f"⚠️  Warning: Could not clear logs: {e}")
    
    # Check if projects exist
    print("\n📊 Checking for existing projects...")
    try:
        projects_response = db.table('projects').select('id', count='exact').execute()
        project_count = projects_response.count
        
        if project_count == 0:
            print("❌ No projects found!")
            print("Please load project data first using:")
            print("  python main.py --load-csv")
            return 1
        
        print(f"✅ Found {project_count} projects")
    except Exception as e:
        print(f"❌ Error checking projects: {e}")
        return 1
    
    # Generate sample data
    print(f"\n🎲 Generating sample data...")
    print(f"   This may take a few minutes for {args.days} days of data...")
    
    try:
        generate_sample_cost_data(db, args.employees, args.days)
        print("\n" + "=" * 60)
        print("✅ Sample data generation completed successfully!")
        print("=" * 60)
        print("\nYou can now:")
        print("  1. Start the server: python main.py --run-server")
        print("  2. Test cost forecasting API:")
        print("     GET /api/v1/cost-forecasting/forecast/1")
        print("  3. View budget alerts:")
        print("     GET /api/v1/cost-forecasting/budget-alerts")
        return 0
        
    except Exception as e:
        print(f"\n❌ Error generating sample data: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())