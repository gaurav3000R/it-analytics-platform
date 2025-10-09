"""
Kaggle Data Loader Module
Handles downloading and loading datasets from Kaggle
"""
import os
import logging
from pathlib import Path
from typing import Optional, Dict, List, Any
import pandas as pd
import kaggle
from kaggle.api.kaggle_api_extended import KaggleApi
import zipfile
import shutil

logger = logging.getLogger(__name__)


class KaggleDataLoader:
    """Load datasets from Kaggle"""
    
    def __init__(self, data_dir: str = "./data/kaggle", kaggle_json_path: Optional[str] = None):
        """
        Initialize Kaggle data loader
        
        Args:
            data_dir: Directory to store downloaded datasets
            kaggle_json_path: Path to kaggle.json credentials file
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup Kaggle API
        self.api = KaggleApi()
        
        # Configure Kaggle credentials
        if kaggle_json_path:
            os.environ['KAGGLE_CONFIG_DIR'] = str(Path(kaggle_json_path).parent)
        
        try:
            self.api.authenticate()
            logger.info("Kaggle API authenticated successfully")
        except Exception as e:
            logger.error(f"Failed to authenticate Kaggle API: {e}")
            logger.info("Please ensure kaggle.json is in ~/.kaggle/ or set KAGGLE_USERNAME and KAGGLE_KEY")
            raise
    
    def download_dataset(
        self, 
        dataset: str, 
        force: bool = False,
        unzip: bool = True
    ) -> Path:
        """
        Download a dataset from Kaggle
        
        Args:
            dataset: Dataset identifier (e.g., 'username/dataset-name')
            force: Force re-download even if exists
            unzip: Automatically unzip downloaded files
            
        Returns:
            Path to downloaded dataset directory
        """
        dataset_name = dataset.split('/')[-1]
        dataset_path = self.data_dir / dataset_name
        
        # Check if already downloaded
        if dataset_path.exists() and not force:
            logger.info(f"Dataset {dataset} already exists at {dataset_path}")
            return dataset_path
        
        # Create dataset directory
        dataset_path.mkdir(parents=True, exist_ok=True)
        
        try:
            logger.info(f"Downloading dataset: {dataset}")
            self.api.dataset_download_files(
                dataset,
                path=str(dataset_path),
                unzip=unzip
            )
            logger.info(f"Dataset downloaded successfully to {dataset_path}")
            return dataset_path
            
        except Exception as e:
            logger.error(f"Error downloading dataset {dataset}: {e}")
            raise
    
    def download_competition_data(
        self,
        competition: str,
        force: bool = False
    ) -> Path:
        """
        Download competition data from Kaggle
        
        Args:
            competition: Competition name
            force: Force re-download even if exists
            
        Returns:
            Path to downloaded competition data directory
        """
        competition_path = self.data_dir / competition
        
        if competition_path.exists() and not force:
            logger.info(f"Competition data {competition} already exists")
            return competition_path
        
        competition_path.mkdir(parents=True, exist_ok=True)
        
        try:
            logger.info(f"Downloading competition data: {competition}")
            self.api.competition_download_files(
                competition,
                path=str(competition_path)
            )
            
            # Unzip all files
            for file in competition_path.glob("*.zip"):
                with zipfile.ZipFile(file, 'r') as zip_ref:
                    zip_ref.extractall(competition_path)
                file.unlink()  # Remove zip file after extraction
            
            logger.info(f"Competition data downloaded to {competition_path}")
            return competition_path
            
        except Exception as e:
            logger.error(f"Error downloading competition {competition}: {e}")
            raise
    
    def list_datasets(self, search: Optional[str] = None, max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Search and list available datasets on Kaggle
        
        Args:
            search: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of dataset metadata
        """
        try:
            datasets = self.api.dataset_list(search=search, page_size=max_results)
            
            results = []
            for dataset in datasets:
                results.append({
                    'ref': dataset.ref,
                    'title': dataset.title,
                    'size': dataset.size,
                    'download_count': dataset.downloadCount,
                    'vote_count': dataset.voteCount,
                    'updated': dataset.lastUpdated
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error listing datasets: {e}")
            return []
    
    def load_csv_from_dataset(
        self,
        dataset: str,
        filename: str,
        force_download: bool = False,
        **pandas_kwargs
    ) -> pd.DataFrame:
        """
        Download dataset and load a specific CSV file
        
        Args:
            dataset: Dataset identifier
            filename: CSV filename to load
            force_download: Force re-download
            **pandas_kwargs: Additional arguments for pd.read_csv
            
        Returns:
            DataFrame with loaded data
        """
        dataset_path = self.download_dataset(dataset, force=force_download)
        csv_path = dataset_path / filename
        
        if not csv_path.exists():
            raise FileNotFoundError(f"File {filename} not found in dataset {dataset}")
        
        logger.info(f"Loading CSV: {csv_path}")
        df = pd.read_csv(csv_path, **pandas_kwargs)
        logger.info(f"Loaded {len(df)} rows from {filename}")
        
        return df
    
    def get_local_datasets(self) -> List[str]:
        """Get list of locally downloaded datasets"""
        if not self.data_dir.exists():
            return []
        
        return [d.name for d in self.data_dir.iterdir() if d.is_dir()]
    
    def clean_dataset(self, dataset_name: str):
        """Remove a downloaded dataset"""
        dataset_path = self.data_dir / dataset_name
        
        if dataset_path.exists():
            shutil.rmtree(dataset_path)
            logger.info(f"Removed dataset: {dataset_name}")
        else:
            logger.warning(f"Dataset {dataset_name} not found")
    
    def clean_all_datasets(self):
        """Remove all downloaded datasets"""
        if self.data_dir.exists():
            shutil.rmtree(self.data_dir)
            self.data_dir.mkdir(parents=True, exist_ok=True)
            logger.info("All datasets removed")


class ProjectDatasetLoader:
    """Load specific datasets for IT project risk analysis"""
    
    # Relevant Kaggle datasets for project management and risk analysis
    RELEVANT_DATASETS = {
        'software_defects': 'semwu/software-defect-prediction',
        'github_commits': 'github/github-commit-data',
        'jira_data': 'rounak41/jira-project-data',
        'agile_metrics': 'niyamatalmass/agile-scrum-project-management',
    }
    
    def __init__(self, data_dir: str = "./data/kaggle"):
        self.loader = KaggleDataLoader(data_dir)
        self.data_dir = Path(data_dir)
    
    def load_software_defects_data(self, force: bool = False) -> Optional[pd.DataFrame]:
        """Load software defect prediction dataset"""
        try:
            logger.info("Loading software defects dataset...")
            dataset = self.RELEVANT_DATASETS.get('software_defects')
            
            if not dataset:
                logger.warning("Software defects dataset not configured")
                return None
            
            # This is an example - actual dataset structure may vary
            df = self.loader.load_csv_from_dataset(
                dataset,
                'defects.csv',  # Adjust filename as needed
                force_download=force
            )
            
            return df
            
        except Exception as e:
            logger.error(f"Error loading software defects data: {e}")
            return None
    
    def search_project_datasets(self, query: str = "project management") -> List[Dict[str, Any]]:
        """Search for project management related datasets"""
        return self.loader.list_datasets(search=query)
    
    def download_custom_dataset(self, dataset_id: str, force: bool = False) -> Path:
        """Download a custom dataset by ID"""
        return self.loader.download_dataset(dataset_id, force=force)


# Utility function for easy access
def quick_load_kaggle_dataset(
    dataset: str,
    filename: Optional[str] = None,
    data_dir: str = "./data/kaggle"
) -> pd.DataFrame:
    """
    Quick function to load a Kaggle dataset
    
    Args:
        dataset: Dataset identifier (e.g., 'username/dataset-name')
        filename: Specific CSV file to load (if None, loads first CSV found)
        data_dir: Directory to store datasets
        
    Returns:
        DataFrame with loaded data
    """
    loader = KaggleDataLoader(data_dir)
    dataset_path = loader.download_dataset(dataset)
    
    # If no filename specified, find first CSV
    if filename is None:
        csv_files = list(dataset_path.glob("*.csv"))
        if not csv_files:
            raise FileNotFoundError(f"No CSV files found in dataset {dataset}")
        filename = csv_files[0].name
    
    return loader.load_csv_from_dataset(dataset, filename)


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    try:
        loader = KaggleDataLoader()
        
        # Search for datasets
        print("\n🔍 Searching for project management datasets...")
        datasets = loader.list_datasets(search="project management", max_results=5)
        
        for i, ds in enumerate(datasets, 1):
            print(f"\n{i}. {ds['title']}")
            print(f"   ID: {ds['ref']}")
            print(f"   Size: {ds['size']}")
            print(f"   Downloads: {ds['download_count']}")
        
        # List local datasets
        print(f"\n📁 Local datasets: {loader.get_local_datasets()}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Setup Instructions:")
        print("1. Sign up at https://www.kaggle.com")
        print("2. Go to Account > API > Create New API Token")
        print("3. Save kaggle.json to ~/.kaggle/kaggle.json")
        print("4. Or set environment variables: KAGGLE_USERNAME and KAGGLE_KEY")
