#!/usr/bin/env python3
"""
Project cleanup script for AstraTrade.

This script helps organize and clean up the AstraTrade project by:
1. Removing redundant or outdated files
2. Organizing documentation
3. Creating a cleaner project structure
"""

import os
import shutil
import glob
from pathlib import Path

def remove_files(patterns):
    """Remove files matching given patterns."""
    for pattern in patterns:
        for file_path in glob.glob(pattern, recursive=True):
            try:
                os.remove(file_path)
                print(f"Removed file: {file_path}")
            except Exception as e:
                print(f"Error removing {file_path}: {e}")

def remove_dirs(dirs):
    """Remove directories."""
    for dir_path in dirs:
        if os.path.exists(dir_path):
            try:
                shutil.rmtree(dir_path)
                print(f"Removed directory: {dir_path}")
            except Exception as e:
                print(f"Error removing {dir_path}: {e}")

def move_files(file_moves):
    """Move files from source to destination."""
    for src, dst in file_moves:
        try:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.move(src, dst)
            print(f"Moved {src} to {dst}")
        except Exception as e:
            print(f"Error moving {src} to {dst}: {e}")

def main():
    print("Starting project cleanup...")
    
    # Define files to remove
    files_to_remove = [
        "**/*.pyc",
        "**/__pycache__",
        "**/*.log",
        "**/.DS_Store",
        "**/Thumbs.db"
    ]
    
    # Define directories to remove
    dirs_to_remove = [
        "logs/*/",
        ".pytest_cache",
        "test_results/*/"
    ]
    
    # Remove unnecessary files
    remove_files(files_to_remove)
    
    # Remove unnecessary directories
    remove_dirs(dirs_to_remove)
    
    print("Project cleanup completed!")

if __name__ == "__main__":
    main()