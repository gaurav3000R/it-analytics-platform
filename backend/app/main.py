"""
Enhanced main entry point with comprehensive setup
"""
import sys
import os
import argparse
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.handler import app
from app.database import SessionLocal, engine, Base
from app.services.data_processor import DataProcessorService
from app.services.csv_loader import CSVLoaderService
from app.services.risk_prediction import RiskPredictionService
from app.services.anomaly_detection import AnomalyDetectionService
from app.services.gemini_service import GeminiAnalyticsService
from app.models.project import Project
from app.models.employee import Employee
from app.models.risk import RiskScore
import uvicorn

def setup_database():
    """Initialize database with all tables"""
    print("Setting up database...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")

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
            for error in result['errors'][:3]:
                print(f"   - {error}")
                
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
    finally:
        db.close()

def train_risk_models():
    """Train ML models for risk prediction"""
    print("Training risk prediction models...")
    
    db = SessionLocal()
    try:
        risk_service = RiskPredictionService()
        metrics = risk_service.train_model(db)
        
        print(f"✅ Risk prediction model trained")
        print(f"   - Test R² Score: {metrics['test_r2']:.3f}")
        print(f"   - Test RMSE: {metrics['test_rmse']:.2f}")
        
        # Save model
        os.makedirs("models", exist_ok=True)
        risk_service.save_model("models/risk_prediction_model.pkl")
        print("✅ Model saved to models/risk_prediction_model.pkl")
        
    except Exception as e:
        print(f"❌ Error training models: {e}")
    finally:
        db.close()

def detect_anomalies():
    """Run anomaly detection on recent data"""
    print("Running anomaly detection...")
    
    db = SessionLocal()
    try:
        anomaly_service = AnomalyDetectionService()
        anomalies = anomaly_service.detect_daily_log_anomalies(db, days_back=30)
        
        print(f"✅ Anomaly detection completed")
        print(f"   - Anomalies detected: {len(anomalies)}")
        
        # Show top anomalies
        for i, anomaly in enumerate(anomalies[:3]):
            print(f"   {i+1}. {anomaly['description']}")
            
    except Exception as e:
        print(f"❌ Error detecting anomalies: {e}")
    finally:
        db.close()

async def generate_ai_insights(project_id: str = None):
    """Generate AI insights using Gemini"""
    print("Generating AI insights...")
    
    db = SessionLocal()
    try:
        gemini_service = GeminiAnalyticsService()
        
        if project_id and project_id.lower() != 'portfolio':
            # Project-specific insights
            print(f"Generating insights for project {project_id}...")
            
            risk_analysis = await gemini_service.generate_project_risk_analysis(db, project_id)
            print(f"✅ Risk analysis generated for {project_id}")
            
            recommendations = await gemini_service.generate_recommendations(db, project_id)
            print(f"✅ Recommendations generated for {project_id}")
            
        else:
            # Portfolio-level insights
            print("Generating portfolio insights...")
            
            portfolio_trends = await gemini_service.analyze_portfolio_trends(db)
            print("✅ Portfolio trends analysis generated")
            
            executive_summary = await gemini_service.generate_executive_summary(db)
            print("✅ Executive summary generated")
            
    except Exception as e:
        print(f"❌ Error generating AI insights: {e}")
        print("💡 Make sure GOOGLE_API_KEY is set in your environment")
    finally:
        db.close()

def show_system_status():
    """Show system status and configuration"""
    print("\n" + "="*50)
    print("IT Analytics Platform - System Status")
    print("="*50)
    
    # Check database
    try:
        db = SessionLocal()
        project_count = db.query(Project).count()
        employee_count = db.query(Employee).count()
        risk_score_count = db.query(RiskScore).count()
        db.close()
        
        print(f"📊 Database Status: CONNECTED")
        print(f"   - Projects: {project_count}")
        print(f"   - Employees: {employee_count}") 
        print(f"   - Risk Scores: {risk_score_count}")
    except Exception as e:
        print(f"📊 Database Status: ERROR - {e}")
    
    # Check Gemini AI
    from app.config import settings
    if settings.GOOGLE_API_KEY:
        print("🤖 Gemini AI: CONFIGURED")
    else:
        print("🤖 Gemini AI: NOT CONFIGURED (set GOOGLE_API_KEY)")
    
    # Check models
    if os.path.exists("models/risk_prediction_model.pkl"):
        print("🧠 ML Models: TRAINED")
    else:
        print("🧠 ML Models: NOT TRAINED (run --train-models)")
    
    print("="*50)

def main():
    parser = argparse.ArgumentParser(description="IT Analytics Platform CLI")
    parser.add_argument("--setup-db", action="store_true", help="Setup database tables")
    parser.add_argument("--load-csv", nargs='?', const="default", help="Load CSV file")
    parser.add_argument("--clear-existing", action="store_true", help="Clear existing data before loading CSV")
    parser.add_argument("--train-models", action="store_true", help="Train ML models")
    parser.add_argument("--detect-anomalies", action="store_true", help="Run anomaly detection")
    parser.add_argument("--ai-insights", help="Generate AI insights (project_id or 'portfolio')")
    parser.add_argument("--status", action="store_true", help="Show system status")
    parser.add_argument("--run-server", action="store_true", help="Run the web server")
    parser.add_argument("--port", type=int, default=8000, help="Port to run server on")
    parser.add_argument("--host", default="0.0.0.0", help="Host to run server on")
    
    args = parser.parse_args()
    
    # Create necessary directories
    os.makedirs("models", exist_ok=True)
    os.makedirs("app/data", exist_ok=True)
    
    # Execute commands
    if args.setup_db:
        setup_database()
    
    if args.load_csv is not None:
        csv_file = None if args.load_csv == "default" else args.load_csv
        load_csv_data(csv_file, args.clear_existing)
    
    if args.train_models:
        train_risk_models()
    
    if args.detect_anomalies:
        detect_anomalies()
    
    if args.ai_insights:
        project_id = None if args.ai_insights.lower() == 'portfolio' else args.ai_insights
        asyncio.run(generate_ai_insights(project_id))
    
    if args.status:
        show_system_status()
    
    # Run server (default if no other commands)
    if args.run_server or not any(vars(args).values()):
        print(f"\n🚀 Starting IT Analytics Platform Server...")
        print(f"   📍 Host: {args.host}")
        print(f"   🔌 Port: {args.port}")
        print(f"   📚 API Docs: http://{args.host}:{args.port}/docs")
        print(f"   🩺 Health: http://{args.host}:{args.port}/health")
        print("\nPress Ctrl+C to stop the server")
        
        uvicorn.run(
            "app.handler:app",
            host=args.host,
            port=args.port,
            reload=True
        )

if __name__ == "__main__":
    main()