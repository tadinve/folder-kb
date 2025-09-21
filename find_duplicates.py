#!/usr/bin/env python3
"""
Script to find duplicate files based on filename and size.
Searches recursively through the workspace directory.
"""

import os
import hashlib
from collections import defaultdict
from pathlib import Path

def get_file_info(file_path):
    """Get file information including name, size, and path."""
    try:
        stat_info = os.stat(file_path)
        return {
            'path': file_path,
            'name': os.path.basename(file_path),
            'size': stat_info.st_size,
            'modified': stat_info.st_mtime
        }
    except (OSError, IOError):
        return None

def find_duplicate_files(root_dir):
    """Find files with identical names and sizes."""
    # Dictionary to group files by (name, size)
    file_groups = defaultdict(list)
    
    # Walk through all files in the directory
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            file_path = os.path.join(root, file)
            file_info = get_file_info(file_path)
            
            if file_info:
                # Use (name, size) as the key
                key = (file_info['name'], file_info['size'])
                file_groups[key].append(file_info)
    
    # Filter to only groups with multiple files (potential duplicates)
    duplicates = {key: files for key, files in file_groups.items() if len(files) > 1}
    
    return duplicates

def format_size(size_bytes):
    """Convert bytes to human readable format."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def print_duplicate_report(duplicates):
    """Print a formatted report of duplicate files."""
    if not duplicates:
        print("✅ No duplicate files found based on name and size!")
        return
    
    print(f"🔍 Found {len(duplicates)} groups of potentially duplicate files:\n")
    
    total_duplicate_files = 0
    total_wasted_space = 0
    
    for i, ((filename, size), file_list) in enumerate(duplicates.items(), 1):
        print(f"Group {i}: '{filename}' ({format_size(size)})")
        print(f"  Found {len(file_list)} copies:")
        
        for file_info in file_list:
            # Show relative path for readability
            rel_path = os.path.relpath(file_info['path'])
            print(f"    📁 {rel_path}")
        
        # Calculate wasted space (all copies except one)
        wasted_space = size * (len(file_list) - 1)
        total_wasted_space += wasted_space
        total_duplicate_files += len(file_list) - 1
        
        if wasted_space > 0:
            print(f"    💾 Potential space savings: {format_size(wasted_space)}")
        
        print()  # Empty line for readability
    
    print("📊 Summary:")
    print(f"  • Total duplicate file groups: {len(duplicates)}")
    print(f"  • Total extra copies: {total_duplicate_files}")
    print(f"  • Potential space savings: {format_size(total_wasted_space)}")

def main():
    """Main function to run the duplicate file analysis."""
    # Get the workspace directory
    workspace_dir = "/Users/venkateshtadinada/Documents/VS-Code-Projects/folder-kb/DocLabs_Sample_Project_Template"
    
    print(f"🔍 Analyzing files in: {workspace_dir}")
    print("Looking for files with identical names and sizes...\n")
    
    # Find duplicates
    duplicates = find_duplicate_files(workspace_dir)
    
    # Print report
    print_duplicate_report(duplicates)

if __name__ == "__main__":
    main()