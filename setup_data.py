"""
Setup Script for Card Database Data Files

This script copies the required data files (CSV files with card BIN ranges)
from the source directory to the application's data directory.
"""
import os
import shutil
from pathlib import Path

def setup_data_files(source_dir: str, target_dir: str = None):
    """
    Copy card data files from source to target directory.
    
    Args:
        source_dir: Directory containing the source CSV files
        target_dir: Target directory (defaults to package data directory)
    """
    # Determine target directory
    if target_dir is None:
        # Default to package data directory
        target_dir = os.path.join(os.path.dirname(__file__), 'data')
    
    # Create target directory if it doesn't exist
    os.makedirs(target_dir, exist_ok=True)
    
    # List of required CSV files
    required_files = [
        'visa-pre.csv',
        'mastercard-pre.csv',
        'amex-pre.csv',
        'discover-pre.csv'
    ]
    
    # Copy each file
    for filename in required_files:
        src_path = os.path.join(source_dir, filename)
        dst_path = os.path.join(target_dir, filename)
        
        try:
            if os.path.exists(src_path):
                shutil.copy2(src_path, dst_path)
                print(f"Copied {filename} to {dst_path}")
            else:
                print(f"Warning: Source file not found: {src_path}")
        except Exception as e:
            print(f"Error copying {filename}: {str(e)}")

if __name__ == "__main__":
    # Get the source directory from user input or use a default
    source_dir = input("Enter the source directory containing card data CSV files: ")
    
    if not source_dir or not os.path.isdir(source_dir):
        print("Invalid source directory. Please provide a valid directory path.")
    else:
        setup_data_files(source_dir)
