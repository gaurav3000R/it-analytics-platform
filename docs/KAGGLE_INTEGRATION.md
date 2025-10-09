# Kaggle Integration Guide

## 🎯 Overview

This guide explains how to integrate Kaggle datasets into the IT Analytics Platform for loading real-world project management and risk data.

## 📦 Installation

Kaggle support has been added to the project dependencies. Install with:

```bash
cd backend
uv sync
# or
pip install -e .
```

This installs:
- `kaggle` - Official Kaggle API client
- `opendatasets` - Simplified dataset downloads

## 🔑 Setup Kaggle API Credentials

### Option 1: Using kaggle.json (Recommended)

1. **Sign up / Login to Kaggle**
   - Visit https://www.kaggle.com
   - Create an account or login

2. **Generate API Token**
   - Go to https://www.kaggle.com/settings
   - Scroll to "API" section
   - Click "Create New API Token"
   - This downloads `kaggle.json` with your credentials

3. **Install Credentials**
   
   **Linux/Mac:**
   ```bash
   mkdir -p ~/.kaggle
   mv ~/Downloads/kaggle.json ~/.kaggle/
   chmod 600 ~/.kaggle/kaggle.json
   ```
   
   **Windows:**
   ```powershell
   mkdir $env:USERPROFILE\.kaggle
   move Downloads\kaggle.json $env:USERPROFILE\.kaggle\
   ```

### Option 2: Using Environment Variables

Add to your `.env` file or export:

```bash
export KAGGLE_USERNAME="your-username"
export KAGGLE_KEY="your-api-key"
```

Or in `.env`:
```env
KAGGLE_USERNAME=your-username
KAGGLE_KEY=your-api-key
```

## 📊 Using the Kaggle Data Loader

### Basic Usage

```python
from app.services.data_loaders import KaggleDataLoader

# Initialize loader
loader = KaggleDataLoader(data_dir="./data/kaggle")

# Download a dataset
dataset_path = loader.download_dataset("username/dataset-name")

# Load a specific CSV file
df = loader.load_csv_from_dataset(
    dataset="username/dataset-name",
    filename="data.csv"
)

print(f"Loaded {len(df)} rows")
```

### Quick Load Function

```python
from app.services.data_loaders import quick_load_kaggle_dataset

# One-line dataset loading
df = quick_load_kaggle_dataset("username/dataset-name", "file.csv")
```

### Search for Datasets

```python
from app.services.data_loaders import KaggleDataLoader

loader = KaggleDataLoader()

# Search for project management datasets
datasets = loader.list_datasets(
    search="project management",
    max_results=10
)

for ds in datasets:
    print(f"{ds['title']} - {ds['ref']}")
    print(f"  Downloads: {ds['download_count']}")
    print(f"  Size: {ds['size']}")
```

### Project-Specific Loader

```python
from app.services.data_loaders import ProjectDatasetLoader

loader = ProjectDatasetLoader()

# Search for relevant datasets
datasets = loader.search_project_datasets("agile project management")

# Download custom dataset
path = loader.download_custom_dataset("username/dataset-name")
```

## 📁 Project Structure

```
it-analytics-platform/
├── backend/
│   ├── app/
│   │   └── services/
│   │       └── data_loaders/
│   │           ├── __init__.py
│   │           └── kaggle_loader.py      # Kaggle integration
│   └── pyproject.toml                    # Updated with Kaggle
├── data/
│   ├── kaggle/                           # Downloaded Kaggle datasets
│   │   ├── dataset-1/
│   │   ├── dataset-2/
│   │   └── ...
│   ├── raw/
│   └── processed/
└── .env.example                          # Updated with Kaggle config
```

## 🎯 Recommended Datasets for Risk Analysis

### Project Management Datasets

1. **Software Defect Prediction**
   - Useful for bug risk modeling
   - Search: "software defect prediction"

2. **GitHub Repository Data**
   - Commit patterns, contributor activity
   - Search: "github repository metrics"

3. **Jira Project Data**
   - Issue tracking, sprint metrics
   - Search: "jira project management"

4. **Agile/Scrum Metrics**
   - Sprint velocity, burndown charts
   - Search: "agile scrum metrics"

5. **Software Engineering Metrics**
   - Code quality, technical debt
   - Search: "software engineering metrics"

## 💻 Example Workflows

### 1. Download and Explore Dataset

```python
from app.services.data_loaders import KaggleDataLoader
import pandas as pd

loader = KaggleDataLoader()

# Download dataset
dataset_path = loader.download_dataset("username/project-metrics")

# List files in dataset
for file in dataset_path.glob("*"):
    print(file.name)

# Load and explore
df = pd.read_csv(dataset_path / "data.csv")
print(df.info())
print(df.head())
```

### 2. Integration with Data Pipeline

```python
from app.services.data_loaders import KaggleDataLoader
from app.services.data_processing import DataPipeline

# Load from Kaggle
loader = KaggleDataLoader()
df = loader.load_csv_from_dataset(
    "username/dataset",
    "projects.csv"
)

# Process with our pipeline
pipeline = DataPipeline()
processed_df = pipeline.process_project_data(df)

# Save to processed directory
processed_df.to_csv("./data/processed/kaggle_projects.csv", index=False)
```

### 3. Train Models with Kaggle Data

```python
from app.services.data_loaders import quick_load_kaggle_dataset
from app.ml.risk_models import MLPipeline

# Load training data from Kaggle
project_data = quick_load_kaggle_dataset(
    "username/project-metrics",
    "metrics.csv"
)

resource_data = quick_load_kaggle_dataset(
    "username/resource-data",
    "resources.csv"
)

# Train models
ml_pipeline = MLPipeline()
results = ml_pipeline.train_all_models(project_data, resource_data)

print("Training complete:", results)
```

### 4. API Endpoint for Kaggle Data

```python
# Add to app/api/risk_routes.py

@router.post("/data/load-kaggle")
async def load_kaggle_dataset(
    dataset_id: str,
    filename: str,
    background_tasks: BackgroundTasks
):
    """Load data from Kaggle dataset"""
    try:
        from app.services.data_loaders import KaggleDataLoader
        
        loader = KaggleDataLoader()
        df = loader.load_csv_from_dataset(dataset_id, filename)
        
        # Process data in background
        background_tasks.add_task(process_and_store_data, df)
        
        return {
            "status": "success",
            "records_loaded": len(df),
            "dataset": dataset_id,
            "filename": filename
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

## 🔍 Finding Relevant Datasets

### Search on Kaggle

1. Visit https://www.kaggle.com/datasets
2. Search for keywords:
   - "project management"
   - "software metrics"
   - "agile scrum"
   - "jira"
   - "github"
   - "bug tracking"
   - "software defects"

### Using API Search

```python
from app.services.data_loaders import KaggleDataLoader

loader = KaggleDataLoader()

# Search terms
searches = [
    "project management",
    "software defects",
    "agile metrics",
    "jira data"
]

for search_term in searches:
    print(f"\n🔍 Results for: {search_term}")
    results = loader.list_datasets(search=search_term, max_results=3)
    
    for ds in results:
        print(f"  • {ds['title']}")
        print(f"    ID: {ds['ref']}")
```

## 🛠️ CLI Tool for Dataset Management

Create a management script:

```python
# scripts/manage_kaggle_data.py
import click
from app.services.data_loaders import KaggleDataLoader

@click.group()
def cli():
    """Kaggle Dataset Management"""
    pass

@cli.command()
@click.argument('query')
@click.option('--max-results', default=10)
def search(query, max_results):
    """Search for datasets"""
    loader = KaggleDataLoader()
    results = loader.list_datasets(query, max_results)
    
    for i, ds in enumerate(results, 1):
        click.echo(f"\n{i}. {ds['title']}")
        click.echo(f"   {ds['ref']}")

@cli.command()
@click.argument('dataset')
def download(dataset):
    """Download a dataset"""
    loader = KaggleDataLoader()
    path = loader.download_dataset(dataset)
    click.echo(f"✅ Downloaded to: {path}")

@cli.command()
def list_local():
    """List downloaded datasets"""
    loader = KaggleDataLoader()
    datasets = loader.get_local_datasets()
    
    click.echo("\n📁 Local Datasets:")
    for ds in datasets:
        click.echo(f"  • {ds}")

if __name__ == '__main__':
    cli()
```

Usage:
```bash
python scripts/manage_kaggle_data.py search "project management"
python scripts/manage_kaggle_data.py download "username/dataset-name"
python scripts/manage_kaggle_data.py list-local
```

## 🧪 Testing Kaggle Integration

```python
# test_kaggle_loader.py
import pytest
from app.services.data_loaders import KaggleDataLoader

def test_kaggle_authentication():
    """Test Kaggle API authentication"""
    loader = KaggleDataLoader()
    assert loader.api is not None

def test_search_datasets():
    """Test dataset search"""
    loader = KaggleDataLoader()
    results = loader.list_datasets("test", max_results=5)
    assert len(results) <= 5

def test_local_datasets():
    """Test listing local datasets"""
    loader = KaggleDataLoader()
    datasets = loader.get_local_datasets()
    assert isinstance(datasets, list)
```

## 📝 Best Practices

1. **Cache Downloads**: Don't re-download datasets unnecessarily
   ```python
   loader.download_dataset("dataset", force=False)  # Uses cached
   ```

2. **Clean Up**: Remove unused datasets to save space
   ```python
   loader.clean_dataset("old-dataset")
   ```

3. **Version Control**: Don't commit large datasets
   ```bash
   # Already in .gitignore
   data/kaggle/
   ```

4. **Document Sources**: Keep track of dataset sources
   ```python
   # datasets.json
   {
     "projects": {
       "source": "username/project-data",
       "downloaded": "2024-01-15",
       "description": "Historical project metrics"
     }
   }
   ```

## 🚨 Troubleshooting

### Authentication Errors

```bash
# Verify credentials
cat ~/.kaggle/kaggle.json

# Check permissions
ls -la ~/.kaggle/kaggle.json
# Should show: -rw------- (600)

# Re-download token from Kaggle if needed
```

### Import Errors

```bash
# Reinstall kaggle package
pip install --upgrade kaggle

# Or with uv
cd backend && uv sync --reinstall-package kaggle
```

### Connection Issues

```python
# Test connection
from kaggle.api.kaggle_api_extended import KaggleApi
api = KaggleApi()
api.authenticate()
print("✅ Connected!")
```

## 📚 Additional Resources

- **Kaggle API Documentation**: https://github.com/Kaggle/kaggle-api
- **Kaggle Datasets**: https://www.kaggle.com/datasets
- **API Reference**: https://www.kaggle.com/docs/api

## 🎯 Next Steps

1. ✅ Install Kaggle package (Done)
2. ✅ Setup credentials
3. 🔄 Search for relevant datasets
4. 🔄 Download and explore data
5. 🔄 Integrate with ML pipeline
6. 🔄 Train models with real data

---

**🎉 Kaggle integration is now ready to use!**
