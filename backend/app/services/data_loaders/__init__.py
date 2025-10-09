"""
Data Loaders Package
Handles loading data from various sources including Kaggle
"""
from .kaggle_loader import (
    KaggleDataLoader,
    ProjectDatasetLoader,
    quick_load_kaggle_dataset
)

__all__ = [
    'KaggleDataLoader',
    'ProjectDatasetLoader',
    'quick_load_kaggle_dataset',
]
