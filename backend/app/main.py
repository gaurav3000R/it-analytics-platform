"""
Main entry point for the IT Analytics Platform with CSV loading and AI insights
"""
import sys
import os
import argparse
import asyncio
from pathlib import Path

# Add the backend directory (parent of app) to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.handler import app
from app.database import SessionLocal
from app.services.data_processor import DataProcessorService
from app.services.csv_loader import CSVLoaderService  # NEW
from app.services.risk_prediction import RiskPredictionService
from app.services.anomaly_detection import AnomalyDetectionService
from app.services.gemini_service import GeminiAnalyticsService  # NEW
import uvicorn

def load_csv_data(csv_file_path: str = None, clear_existing: bool = False):
    """Load CSV data into database"""
    print("Loading CSV data...")
    
    db = SessionLocal()
    try:
        csv_loader = CSVLoaderService()
        result = csv_loader.csv_to_database(db, csv_file_path, clear_existing)
        
        print(f"✅ CSV data loaded successfully")
        print(f"   - Projects created: {result['projects_created']}")
        print(f"   - Projects updated: {result['projects_updated']}")
        print(f"   - Success rate: {result['success_rate']:.1f}%")
        
        if result['errors']:
            print(f"⚠️  Errors encountered: {len(result['errors'])}")
            for error in result['errors'][:3]:  # Show first 3 errors
                print(f"   - {error}")
                
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
    finally:
        db.close()

def setup_sample_data():
    """Setup sample data for development/demo"""
    print("Setting up sample data...")
    
    db = SessionLocal()
    try:
        data_processor = DataProcessorService()
        data_processor.generate_sample_data(db, num_projects=10, num_employees=20)
        print("✅ Sample data created successfully")
    finally:
        db.close()

def train_models():
    """Train ML models"""
    print("Training ML models...")
    
    db = SessionLocal()
    try:
        # Train risk prediction model
        risk_service = RiskPredictionService()
        metrics = risk_service.train_model(db)
        print(f"✅ Risk prediction model trained - R2: {metrics['test_r2']:.3f}")
        
        # Save model
        risk_service.save_model("models/risk_prediction_model.pkl")
        print("✅ Risk prediction model saved")
        
        # Run anomaly detection
        anomaly_service = AnomalyDetectionService()
        anomalies = anomaly_service.detect_daily_log_anomalies(db, days_back=30)
        print(f"✅ Anomaly detection completed - Found {len(anomalies)} anomalies")
        
    finally:
        db.close()

async def generate_ai_insights(project_id: str = None):
    """Generate AI insights for projects"""
    print("Generating AI insights...")
    
    db = SessionLocal()
    try:
        gemini_service = GeminiAnalyticsService()
        
        if project_id:
            # Generate insights for specific project
            print(f"Generating insights for project {project_id}...")
            
            risk_analysis = await gemini_service.generate_project_risk_analysis(db, project_id)
            print(f"✅ Risk analysis generated for {project_id}")
            
            recommendations = await gemini_service.generate_recommendations(db, project_id)
            print(f"✅ Recommendations generated for {project_id}")
            
        else:
            # Generate portfolio-level insights
            print("Generating portfolio insights...")
            
            portfolio_trends = await gemini_service.analyze_portfolio_trends(db)
            print("✅ Portfolio trends analysis generated")
            
            executive_summary = await gemini_service.generate_executive_summary(db)
            print("✅ Executive summary generated")
            
    except Exception as e:
        print(f"❌ Error generating AI insights: {e}")
        print("Make sure GOOGLE_API_KEY is set in your environment")
    finally:
        db.close()

def show_csv_summary():
    """Show summary of CSV data"""
    print("CSV Data Summary")
    print("=" * 50)
    
    try:
        csv_loader = CSVLoaderService()
        df = csv_loader.load_csv_data()
        summary = csv_loader.get_data_summary(df)
        
        print(f"Total Records: {summary['total_records']}")
        print(f"Columns: {len(summary['columns'])}")
        print("\nRisk Level Distribution:")
        for risk_level, count in summary['risk_level_distribution'].items():
            print(f"  {risk_level}: {count}")
        
        print("\nProject Type Distribution:")
        for project_type, count in list(summary['project_type_distribution'].items())[:5]:
            print(f"  {project_type}: {count}")
            
        print(f"\nColumns with missing values:")
        missing_values = {k: v for k, v in summary['missing_values'].items() if v > 0}
        if missing_values:
            for col, count in list(missing_values.items())[:5]:
                print(f"  {col}: {count}")
        else:
            print("  None")
        
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")

def main():
    parser = argparse.ArgumentParser(description="IT Analytics Platform CLI")
    parser.add_argument("--load-csv", nargs='?', default=None, help="Load CSV file (default: app/data/project_risk_dataset.csv)")  # FIXED
    parser.add_argument("--clear-existing", action="store_true", help="Clear existing projects before loading CSV")
    parser.add_argument("--csv-summary", action="store_true", help="Show CSV data summary")
    parser.add_argument("--setup-data", action="store_true", help="Setup sample data (legacy)")
    parser.add_argument("--train-models", action="store_true", help="Train ML models")
    parser.add_argument("--ai-insights", help="Generate AI insights (provide project_id or 'portfolio')")
    parser.add_argument("--run-server", action="store_true", help="Run the server")
    parser.add_argument("--port", type=int, default=8000, help="Port to run server on")
    parser.add_argument("--host", default="0.0.0.0", help="Host to run server on")
    
    args = parser.parse_args()
    
    # Create models directory if it doesn't exist
    os.makedirs("models", exist_ok=True)
    os.makedirs("app/data", exist_ok=True)
    
    # CSV operations
    if args.csv_summary:
        show_csv_summary()
        return
    
    if args.load_csv is not None or args.clear_existing:  # FIXED: Trigger on flag or clear
        csv_file = args.load_csv if args.load_csv else None  # Use default if None
        load_csv_data(csv_file, args.clear_existing)
    
    # Legacy sample data
    if args.setup_data:
        setup_sample_data()
    
    # ML training
    if args.train_models:
        train_models()
    
    # AI insights generation
    if args.ai_insights:
        project_id = None if args.ai_insights.lower() == 'portfolio' else args.ai_insights
        asyncio.run(generate_ai_insights(project_id))
    
    # Run server
    if args.run_server or (not any([args.load_csv is not None, args.csv_summary, args.setup_data, 
                                   args.train_models, args.ai_insights])):
        print(f"Starting server on {args.host}:{args.port}...")
        print(f"API Documentation: http://{args.host}:{args.port}/docs")
        uvicorn.run(
            "app.handler:app",
            host=args.host,
            port=args.port,
            reload=True
        )

if __name__ == "__main__":
    main()