#!/usr/bin/env python3
"""
Script to generate sample cost data for a SUBSET of projects
This is more practical for large datasets (e.g., 4000 projects)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import connect_db
from app.utils.generate_cost_sample_data import CostSampleDataGenerator
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="Generate sample cost data for a subset of projects"
    )
    parser.add_argument(
        "--employees",
        type=int,
        default=35,
        help="Number of employees to create (default: 35)"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=45,
        help="Days of historical data to generate (default: 45)"
    )
    parser.add_argument(
        "--max-projects",
        type=int,
        default=500,
        help="Maximum number of projects to generate data for (default: 500)"
    )
    parser.add_argument(
        "--project-selection",
        choices=['random', 'high-budget', 'high-risk', 'first-n'],
        default='random',
        help="How to select projects (default: random)"
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
    print("Cost Forecasting Sample Data Generator (SUBSET MODE)")
    print("=" * 60)
    print(f"Employees to create: {args.employees}")
    print(f"Days of history: {args.days}")
    print(f"Max projects: {args.max_projects}")
    print(f"Selection method: {args.project_selection}")
    
    # Calculate estimated records
    estimated_logs = args.max_projects * args.days * 3  # ~3 logs per project per day
    print(f"\n📊 Estimated daily log records: ~{estimated_logs:,}")
    print(f"⏱️  Estimated time: ~{int(estimated_logs / 5000)} minutes")
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
    
    # Get and filter projects
    print(f"\n📊 Fetching projects with '{args.project_selection}' selection...")
    try:
        all_projects_response = db.table('projects').select(
            'id, project_id, name, project_budget_usd, team_size, '
            'complexity_score, risk_level'
        ).execute()
        
        all_projects = all_projects_response.data
        total_projects = len(all_projects)
        
        if total_projects == 0:
            print("❌ No projects found!")
            print("Please load project data first using:")
            print("  python main.py --load-csv")
            return 1
        
        print(f"✅ Found {total_projects} total projects")
        
        # Select subset based on criteria
        selected_projects = select_projects(
            all_projects, 
            args.max_projects, 
            args.project_selection
        )
        
        print(f"✅ Selected {len(selected_projects)} projects for data generation")
        
        # Show selection summary
        if args.project_selection == 'high-budget':
            avg_budget = sum(p.get('project_budget_usd', 0) or 0 for p in selected_projects) / len(selected_projects)
            print(f"   Average budget: ${avg_budget:,.2f}")
        elif args.project_selection == 'high-risk':
            risk_dist = {}
            for p in selected_projects:
                risk = p.get('risk_level', 'Unknown')
                risk_dist[risk] = risk_dist.get(risk, 0) + 1
            print(f"   Risk distribution: {risk_dist}")
        
    except Exception as e:
        print(f"❌ Error fetching projects: {e}")
        return 1
    
    # Generate sample data using the subset
    print(f"\n🎲 Generating sample data...")
    print(f"   This may take a few minutes...")
    
    try:
        generator = CostSampleDataGenerator(db)
        
        # Create employees
        print("\n1️⃣  Creating employees...")
        employees = generator._create_sample_employees(args.employees)
        print(f"✅ Created {len(employees)} employees")
        
        # Generate daily logs for selected projects only
        print(f"\n2️⃣  Generating daily logs for {len(selected_projects)} projects...")
        generator._generate_daily_logs(selected_projects, employees, args.days)
        print(f"✅ Generated daily logs for {args.days} days")
        
        # Update project dates and spend
        print("\n3️⃣  Updating project dates and spending...")
        generator._update_project_dates_and_spend(selected_projects, args.days)
        print("✅ Updated project dates and spending")
        
        print("\n" + "=" * 60)
        print("✅ Sample data generation completed successfully!")
        print("=" * 60)
        print("\nYou can now:")
        print("  1. Start the server: python main.py --run-server")
        print("  2. Test cost forecasting API:")
        print(f"     GET /api/v1/cost-forecasting/forecast/{selected_projects[0]['id']}")
        print("  3. View budget alerts:")
        print("     GET /api/v1/cost-forecasting/budget-alerts")
        print("\nNote: Forecasting will only work for the selected projects with data.")
        return 0
        
    except Exception as e:
        print(f"\n❌ Error generating sample data: {e}")
        import traceback
        traceback.print_exc()
        return 1


def select_projects(projects, max_count, method):
    """Select a subset of projects based on the specified method"""
    import random
    
    if len(projects) <= max_count:
        return projects
    
    if method == 'random':
        return random.sample(projects, max_count)
    
    elif method == 'high-budget':
        # Sort by budget and take top N
        sorted_projects = sorted(
            projects, 
            key=lambda p: p.get('project_budget_usd', 0) or 0, 
            reverse=True
        )
        return sorted_projects[:max_count]
    
    elif method == 'high-risk':
        # Prioritize High and Very High risk projects
        risk_priority = {'Very High': 4, 'High': 3, 'Medium': 2, 'Low': 1, 'Very Low': 0}
        sorted_projects = sorted(
            projects,
            key=lambda p: risk_priority.get(p.get('risk_level', 'Medium'), 2),
            reverse=True
        )
        return sorted_projects[:max_count]
    
    elif method == 'first-n':
        return projects[:max_count]
    
    return projects[:max_count]


if __name__ == "__main__":
    exit(main())