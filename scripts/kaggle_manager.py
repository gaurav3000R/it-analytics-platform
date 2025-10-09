#!/usr/bin/env python3
"""
Kaggle Dataset Management CLI
Quick tool for searching, downloading, and managing Kaggle datasets
"""
import sys
import argparse
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from app.services.data_loaders import KaggleDataLoader, ProjectDatasetLoader
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def search_datasets(args):
    """Search for datasets on Kaggle"""
    try:
        loader = KaggleDataLoader()
        results = loader.list_datasets(
            search=args.query,
            max_results=args.max_results
        )
        
        if not results:
            print(f"No datasets found for query: {args.query}")
            return
        
        print(f"\n🔍 Found {len(results)} datasets for '{args.query}':\n")
        print("=" * 80)
        
        for i, ds in enumerate(results, 1):
            print(f"\n{i}. {ds['title']}")
            print(f"   📦 Dataset ID: {ds['ref']}")
            print(f"   📊 Size: {ds['size']}")
            print(f"   📥 Downloads: {ds['download_count']:,}")
            print(f"   👍 Votes: {ds['vote_count']:,}")
            print(f"   🕒 Updated: {ds['updated']}")
        
        print("\n" + "=" * 80)
        print(f"\n💡 To download: python {sys.argv[0]} download <dataset-id>")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Make sure Kaggle credentials are configured")
        print("   Run: python scripts/kaggle_manager.py setup")


def download_dataset(args):
    """Download a dataset from Kaggle"""
    try:
        loader = KaggleDataLoader(data_dir=args.data_dir)
        
        print(f"\n📥 Downloading dataset: {args.dataset}")
        print("   This may take a while depending on dataset size...")
        
        dataset_path = loader.download_dataset(
            args.dataset,
            force=args.force,
            unzip=not args.keep_zip
        )
        
        print(f"\n✅ Dataset downloaded successfully!")
        print(f"   Location: {dataset_path}")
        
        # List files
        files = list(dataset_path.glob("*"))
        print(f"\n📁 Files in dataset ({len(files)}):")
        for file in files[:10]:  # Show first 10 files
            size = file.stat().st_size / (1024 * 1024)  # MB
            print(f"   • {file.name} ({size:.2f} MB)")
        
        if len(files) > 10:
            print(f"   ... and {len(files) - 10} more files")
        
        return dataset_path
        
    except Exception as e:
        print(f"❌ Error downloading dataset: {e}")
        sys.exit(1)


def list_local(args):
    """List locally downloaded datasets"""
    try:
        loader = KaggleDataLoader(data_dir=args.data_dir)
        datasets = loader.get_local_datasets()
        
        if not datasets:
            print("\n📁 No local datasets found")
            print(f"   Location: {loader.data_dir}")
            return
        
        print(f"\n📁 Local datasets in {loader.data_dir}:")
        print("=" * 80)
        
        for i, dataset in enumerate(datasets, 1):
            dataset_path = loader.data_dir / dataset
            
            # Count files
            files = list(dataset_path.glob("*"))
            size = sum(f.stat().st_size for f in files if f.is_file())
            size_mb = size / (1024 * 1024)
            
            print(f"\n{i}. {dataset}")
            print(f"   📊 Files: {len(files)}")
            print(f"   💾 Size: {size_mb:.2f} MB")
            print(f"   📂 Path: {dataset_path}")
        
        print("\n" + "=" * 80)
        print(f"\n💡 Total datasets: {len(datasets)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def setup_wizard(args):
    """Interactive setup wizard"""
    print("\n" + "=" * 80)
    print("  🚀 Kaggle Integration Setup Wizard")
    print("=" * 80)
    
    print("\n📚 Step 1: Get Kaggle API Credentials")
    print("   1. Go to https://www.kaggle.com/settings")
    print("   2. Scroll to 'API' section")
    print("   3. Click 'Create New API Token'")
    print("   4. Save the downloaded kaggle.json file")
    
    input("\n   Press Enter when you have your kaggle.json file...")
    
    print("\n📁 Step 2: Install Credentials")
    print("   The kaggle.json file should be placed at:")
    print("   Linux/Mac: ~/.kaggle/kaggle.json")
    print("   Windows: %USERPROFILE%\\.kaggle\\kaggle.json")
    
    print("\n🧪 Step 3: Test Connection")
    try:
        loader = KaggleDataLoader()
        print("   ✅ Kaggle API authenticated successfully!")
        
        # Test search
        print("\n   Testing search...")
        results = loader.list_datasets("test", max_results=3)
        print(f"   ✅ Found {len(results)} datasets")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print("\n   💡 Make sure kaggle.json is in the correct location")
        return
    
    print("\n" + "=" * 80)
    print("  ✅ Setup Complete!")
    print("=" * 80)
    print("\n💡 Try these commands:")
    print(f"   python {sys.argv[0]} search 'project management'")
    print(f"   python {sys.argv[0]} list")


def main():
    parser = argparse.ArgumentParser(
        description="Kaggle Dataset Management Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search for datasets
  python %(prog)s search "project management"
  
  # Download a dataset
  python %(prog)s download username/dataset-name
  
  # List local datasets
  python %(prog)s list
  
  # Setup wizard
  python %(prog)s setup
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search for datasets')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--max-results', type=int, default=10, help='Maximum results')
    search_parser.set_defaults(func=search_datasets)
    
    # Download command
    download_parser = subparsers.add_parser('download', help='Download a dataset')
    download_parser.add_argument('dataset', help='Dataset ID (username/dataset-name)')
    download_parser.add_argument('--force', action='store_true', help='Force re-download')
    download_parser.add_argument('--keep-zip', action='store_true', help='Keep zip files')
    download_parser.add_argument('--data-dir', default='./data/kaggle', help='Data directory')
    download_parser.set_defaults(func=download_dataset)
    
    # List command
    list_parser = subparsers.add_parser('list', help='List local datasets')
    list_parser.add_argument('--data-dir', default='./data/kaggle', help='Data directory')
    list_parser.set_defaults(func=list_local)
    
    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Interactive setup wizard')
    setup_parser.set_defaults(func=setup_wizard)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    args.func(args)


if __name__ == '__main__':
    main()
