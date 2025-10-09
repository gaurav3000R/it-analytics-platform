# 🚀 Kaggle Quick Start

## ✅ Status: Installed & Ready

Kaggle API is installed. You just need to add your credentials to start loading data.

---

## 🔑 Setup Credentials (One-Time)

### Step 1: Get Your API Token
1. Visit: https://www.kaggle.com/settings
2. Scroll to **"API"** section
3. Click **"Create New Token"**
4. Downloads `kaggle.json`

### Step 2: Install Credentials
```bash
mkdir -p ~/.kaggle
mv ~/Downloads/kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json
```

### Step 3: Verify Setup
```bash
python verify_kaggle.py
```

---

## 💻 Usage Examples

### CLI - Quick Commands
```bash
# Search for datasets
python scripts/kaggle_manager.py search "project management"

# Download a dataset
python scripts/kaggle_manager.py download username/dataset-name

# List local datasets
python scripts/kaggle_manager.py list
```

### Python - Quick Code
```python
from app.services.data_loaders import quick_load_kaggle_dataset

# One-liner to load data
df = quick_load_kaggle_dataset("username/dataset", "file.csv")
```

### Python - Full Control
```python
from app.services.data_loaders import KaggleDataLoader

loader = KaggleDataLoader()

# Search
datasets = loader.list_datasets("software defects", max_results=10)

# Download
path = loader.download_dataset("username/dataset-name")

# Load CSV
df = loader.load_csv_from_dataset("username/dataset", "data.csv")
```

---

## 🔍 Useful Searches

```bash
# Project Management
python scripts/kaggle_manager.py search "project management metrics"
python scripts/kaggle_manager.py search "agile scrum"

# Software Quality
python scripts/kaggle_manager.py search "software defect prediction"
python scripts/kaggle_manager.py search "bug tracking"

# Development
python scripts/kaggle_manager.py search "github repository metrics"
python scripts/kaggle_manager.py search "code quality"
```

---

## 📁 Where Data is Stored

```
data/kaggle/
├── username-dataset1/
│   └── data.csv
└── username-dataset2/
    └── metrics.csv
```

*(Automatically excluded from Git)*

---

## 🆘 Troubleshooting

### Can't find kaggle.json?
```bash
ls -la ~/.kaggle/kaggle.json
# If not found, follow Setup Credentials above
```

### Permission error?
```bash
chmod 600 ~/.kaggle/kaggle.json
```

### Import error?
```bash
cd backend && uv sync
```

---

## 📚 Full Documentation

- **Complete Guide**: `KAGGLE_INSTALLATION_GUIDE.md`
- **Status Report**: `KAGGLE_SETUP_STATUS.md`
- **API Reference**: `docs/KAGGLE_INTEGRATION.md`

---

## ⚡ TL;DR

```bash
# 1. Get token from https://www.kaggle.com/settings
# 2. Install it:
mkdir -p ~/.kaggle && mv ~/Downloads/kaggle.json ~/.kaggle/ && chmod 600 ~/.kaggle/kaggle.json

# 3. Verify:
python verify_kaggle.py

# 4. Start using:
python scripts/kaggle_manager.py search "your topic"
```

**That's it! You're ready to load data! 🎉**
