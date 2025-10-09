# 📦 Kaggle Installation & Setup Guide

## ✅ Installation Complete!

Kaggle has been successfully installed in your IT Analytics Platform. This guide will help you complete the setup and start loading data.

---

## 📋 What Was Installed

### Packages
- ✅ **kaggle** (v1.7.4.5) - Official Kaggle API client
- ✅ **opendatasets** (v0.1.22) - Simplified dataset downloads *(Note: May have Python 3.13 compatibility issues)*

### Project Structure
```
it-analytics-platform/
├── backend/
│   ├── app/
│   │   └── services/
│   │       └── data_loaders/          ✅ Custom data loaders
│   │           ├── __init__.py
│   │           └── kaggle_loader.py   ✅ Kaggle integration
│   └── pyproject.toml                 ✅ Updated dependencies
│
├── data/
│   └── kaggle/                        ✅ Downloaded datasets storage
│
├── scripts/
│   └── kaggle_manager.py              ✅ CLI management tool
│
├── docs/
│   └── KAGGLE_INTEGRATION.md          ✅ Complete documentation
│
├── verify_kaggle.py                   ✅ Verification script
└── setup_kaggle.py                    ✅ Interactive setup tool
```

---

## 🚀 Quick Start (3 Steps)

### Step 1: Verify Installation

```bash
cd backend
uv run python ../verify_kaggle.py
```

This will check:
- ✅ Kaggle package installation
- ✅ Project structure
- ⚠️  Credentials status
- ✅ Custom loaders

### Step 2: Setup Kaggle Credentials

#### Option A: Get Your API Token

1. Go to [https://www.kaggle.com/settings](https://www.kaggle.com/settings)
2. Scroll down to the **"API"** section
3. Click **"Create New Token"**
4. This downloads `kaggle.json` to your Downloads folder

#### Option B: Install the Credentials

```bash
# Create the Kaggle directory
mkdir -p ~/.kaggle

# Move the downloaded file
mv ~/Downloads/kaggle.json ~/.kaggle/

# Set correct permissions (required for security)
chmod 600 ~/.kaggle/kaggle.json
```

#### Option C: Manual Setup

Create `~/.kaggle/kaggle.json` manually:

```json
{
  "username": "your_kaggle_username",
  "key": "your_api_key_here"
}
```

Then set permissions:
```bash
chmod 600 ~/.kaggle/kaggle.json
```

### Step 3: Test Connection

```bash
# Verify everything works
cd backend
uv run python ../verify_kaggle.py

# Test with a search
cd ..
python scripts/kaggle_manager.py search "project management"
```

---

## 💻 Usage Examples

### 1. Using the CLI Tool

The simplest way to interact with Kaggle:

```bash
# Search for datasets
python scripts/kaggle_manager.py search "software defects"
python scripts/kaggle_manager.py search "agile metrics" --max-results 20

# Download a dataset
python scripts/kaggle_manager.py download username/dataset-name

# List downloaded datasets
python scripts/kaggle_manager.py list
```

### 2. Using Python API

For programmatic access in your code:

```python
from app.services.data_loaders import KaggleDataLoader

# Initialize loader
loader = KaggleDataLoader()

# Search for datasets
datasets = loader.list_datasets("project management", max_results=10)
for ds in datasets:
    print(f"{ds['title']} - {ds['ref']}")

# Download a dataset
dataset_path = loader.download_dataset("username/dataset-name")

# Load CSV directly into pandas
df = loader.load_csv_from_dataset("username/dataset", "data.csv")
```

### 3. Quick Load Function

One-liner to load data:

```python
from app.services.data_loaders import quick_load_kaggle_dataset

# Load data directly
df = quick_load_kaggle_dataset("username/dataset", "metrics.csv")
```

### 4. Integration with Existing Pipeline

Combine Kaggle data with your existing data processing:

```python
from app.services.data_loaders import KaggleDataLoader
from app.services.data_processing import DataPipeline
from app.ml.risk_models import MLPipeline

# Load from Kaggle
loader = KaggleDataLoader()
raw_data = loader.load_csv_from_dataset("username/project-data", "metrics.csv")

# Process with existing pipeline
pipeline = DataPipeline()
processed_data = pipeline.process_project_data(raw_data)

# Train ML models
ml_pipeline = MLPipeline()
results = ml_pipeline.train_all_models(processed_data, resource_data)
```

---

## 🎯 Relevant Datasets for IT Analytics

Here are some search queries to find relevant datasets:

### Project Management
- `"project management metrics"`
- `"agile scrum data"`
- `"sprint velocity"`
- `"project tracking"`

### Software Quality
- `"software defect prediction"`
- `"bug tracking data"`
- `"code quality metrics"`
- `"technical debt"`

### Development Metrics
- `"github repository metrics"`
- `"git commit analysis"`
- `"developer productivity"`
- `"code review data"`

### IT Operations
- `"incident management"`
- `"service desk tickets"`
- `"IT service management"`
- `"system downtime"`

---

## 🔧 CLI Commands Reference

### Search
```bash
python scripts/kaggle_manager.py search "query"
python scripts/kaggle_manager.py search "query" --max-results 20
```

### Download
```bash
python scripts/kaggle_manager.py download username/dataset-name
python scripts/kaggle_manager.py download username/dataset --force  # Re-download
```

### List
```bash
python scripts/kaggle_manager.py list
python scripts/kaggle_manager.py list --data-dir ./custom/path
```

---

## 📂 Data Storage Structure

Downloaded datasets are stored in:
```
data/kaggle/
├── username-dataset1/
│   ├── data.csv
│   ├── metadata.json
│   └── README.md
├── username-dataset2/
│   └── train.csv
└── ...
```

This directory is:
- ✅ Automatically created when downloading
- ✅ Excluded from Git (in .gitignore)
- ✅ Cached to avoid re-downloading

---

## 🔒 Security & Best Practices

### Security
- ✅ `kaggle.json` must have 600 permissions (user read/write only)
- ✅ Never commit credentials to Git
- ✅ `data/kaggle/` is gitignored to prevent committing large datasets
- ✅ Credentials stored in `~/.kaggle/` (outside project directory)

### Best Practices

1. **Use Caching**: Don't re-download unnecessarily
   ```python
   loader.download_dataset("dataset", force=False)
   ```

2. **Search Before Download**: Verify dataset ID and content
   ```bash
   python scripts/kaggle_manager.py search "keyword"
   ```

3. **Document Your Data Sources**: Keep track of what you download
   - Add dataset info to a `data/README.md`
   - Note the dataset ID and download date
   - Document any preprocessing steps

4. **Clean Up**: Remove unused datasets to save space
   ```bash
   rm -rf data/kaggle/old-dataset-name
   ```

---

## 🧪 Testing Your Setup

### Test 1: Import Verification
```bash
cd backend
uv run python -c "from app.services.data_loaders import KaggleDataLoader; print('✅ Import successful!')"
```

### Test 2: Search Functionality
```bash
python scripts/kaggle_manager.py search "test" --max-results 3
```

### Test 3: Load Sample Data
```python
from app.services.data_loaders import KaggleDataLoader

loader = KaggleDataLoader()
datasets = loader.list_datasets("machine learning", max_results=5)
print(f"✅ Found {len(datasets)} datasets")
```

---

## 🚨 Troubleshooting

### Issue: "No module named 'kaggle'"
**Solution:**
```bash
cd backend
uv sync
```

### Issue: "Could not find kaggle.json"
**Solution:**
```bash
# Check if file exists
ls -la ~/.kaggle/kaggle.json

# If not, create it
mkdir -p ~/.kaggle
# Then add your credentials (see Step 2 above)
```

### Issue: "403 Forbidden" or Authentication Errors
**Solution:**
- Verify your credentials at https://www.kaggle.com/settings
- Create a new API token
- Replace `~/.kaggle/kaggle.json` with the new token
- Check permissions: `chmod 600 ~/.kaggle/kaggle.json`

### Issue: "Dataset not found"
**Solution:**
```bash
# Verify the dataset ID is correct
python scripts/kaggle_manager.py search "dataset name"

# Use the exact ID from search results
```

### Issue: "Permission denied"
**Solution:**
```bash
# Fix permissions
chmod 600 ~/.kaggle/kaggle.json
```

### Issue: OpenDatasets Import Error (Python 3.13)
**Solution:**
OpenDatasets has compatibility issues with Python 3.13. Use Kaggle's official API instead:
```python
# Instead of opendatasets.download()
# Use KaggleDataLoader
from app.services.data_loaders import KaggleDataLoader
loader = KaggleDataLoader()
loader.download_dataset("username/dataset")
```

---

## 📚 Additional Resources

### Documentation
- **Kaggle API Docs**: https://github.com/Kaggle/kaggle-api
- **Project Integration Guide**: `docs/KAGGLE_INTEGRATION.md`
- **Complete Setup**: `KAGGLE_SETUP_COMPLETE.md`

### Example Notebooks
- Create notebooks in `notebooks/` directory
- Example: `notebooks/kaggle_data_exploration.ipynb`

### API Reference
See `backend/app/services/data_loaders/kaggle_loader.py` for:
- `KaggleDataLoader` - Main loader class
- `ProjectDatasetLoader` - Project-specific loaders
- Helper functions and utilities

---

## ✅ Verification Checklist

Before you start using Kaggle:

- [ ] Kaggle package installed (`uv sync` completed)
- [ ] Credentials configured (`~/.kaggle/kaggle.json` exists)
- [ ] Permissions set correctly (600)
- [ ] Verification script passes (`python verify_kaggle.py`)
- [ ] Can search datasets (`python scripts/kaggle_manager.py search "test"`)
- [ ] Project structure in place (`data/kaggle/` directory exists)
- [ ] Custom loaders importable

---

## 🎉 You're Ready!

Kaggle is now installed and configured. You can:

1. ✅ Search thousands of datasets
2. ✅ Download data automatically
3. ✅ Load data into pandas DataFrames
4. ✅ Integrate with your ML pipeline
5. ✅ Use CLI tools for quick management

### Quick Command Reference

```bash
# Verify setup
python verify_kaggle.py

# Search datasets
python scripts/kaggle_manager.py search "your query"

# Download data
python scripts/kaggle_manager.py download dataset-id

# In Python
from app.services.data_loaders import quick_load_kaggle_dataset
df = quick_load_kaggle_dataset("dataset-id", "file.csv")
```

---

## 📞 Need Help?

- Check `docs/KAGGLE_INTEGRATION.md` for detailed examples
- Run `python verify_kaggle.py` to diagnose issues
- Review error messages for specific solutions

**Happy data loading! 🚀**
