#!/usr/bin/env python3
"""
Generate enhanced sample data for better model training
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal
from app.services.data_processor import DataProcessorService

def generate_enhanced_data():
    """Generate more realistic and varied sample data"""
    db = SessionLocal()
    try:
        data_processor = DataProcessorService()
        
        # Generate more projects with varied characteristics
        print("Generating enhanced sample data...")
        data_processor.generate_sample_data(db, num_projects=50, num_employees=30)
        print("✅ Enhanced data generated successfully")
        
    except Exception as e:
        print(f"❌ Error generating data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    generate_enhanced_data()