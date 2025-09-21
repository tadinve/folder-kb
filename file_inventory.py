#!/usr/bin/env python3
"""
File Inventory Generator

This script creates a comprehensive inventory of all files in a directory
and saves the information to a CSV file using pandas.

FEATURES:
- Recursive directory scanning
- Full file path information
- File size and modification dates
- File type detection
- CSV export with pandas
- Human-readable file sizes

OUTPUT COLUMNS:
- full_path: Complete file path
- directory: Directory containing the file
- filename: File name with extension
- file_type: File extension/type
- size_bytes: File size in bytes
- size_human: File size in human-readable format
- modified_date: Last modification date
- created_date: Creation date (where available)
"""

import os
import pandas as pd
from pathlib import Path
from datetime import datetime
import argparse

def format_size(size_bytes):
    """Convert bytes to human readable format."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def get_file_type(filename):
    """Extract file type/extension from filename."""
    if '.' not in filename:
        return "no_extension"
    
    extension = filename.split('.')[-1].lower()
    return extension if extension else "no_extension"

def scan_directory(directory_path, exclude_dirs=None):
    """
    Recursively scan directory and collect file information.
    
    Args:
        directory_path: Path to scan
        exclude_dirs: Set of directory names to exclude
    
    Returns:
        List of dictionaries with file information
    """
    if exclude_dirs is None:
        exclude_dirs = {'.git', '.venv', 'node_modules', '__pycache__', '.pytest_cache'}
    
    file_data = []
    directory_path = Path(directory_path)
    
    print(f"🔍 Scanning directory: {directory_path}")
    
    for root, dirs, files in os.walk(directory_path):
        # Filter out excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        root_path = Path(root)
        
        for filename in files:
            try:
                file_path = root_path / filename
                stat_info = file_path.stat()
                
                # Collect file information
                file_info = {
                    'full_path': str(file_path.absolute()),
                    'directory': str(root_path.absolute()),
                    'filename': filename,
                    'file_type': get_file_type(filename),
                    'size_bytes': stat_info.st_size,
                    'size_human': format_size(stat_info.st_size),
                    'modified_date': datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                    'created_date': datetime.fromtimestamp(stat_info.st_ctime).isoformat()
                }
                
                file_data.append(file_info)
                
            except (OSError, IOError, PermissionError) as e:
                print(f"⚠️  Skipping {file_path}: {e}")
                continue
    
    print(f"📊 Found {len(file_data)} files")
    return file_data

def create_file_inventory(directory_path, output_file=None, include_stats=True):
    """
    Create a comprehensive file inventory and save to CSV.
    
    Args:
        directory_path: Directory to scan
        output_file: Output CSV filename (auto-generated if None)
        include_stats: Whether to include summary statistics
    
    Returns:
        pandas DataFrame with file information
    """
    # Scan directory
    file_data = scan_directory(directory_path)
    
    if not file_data:
        print("❌ No files found!")
        return None
    
    # Create DataFrame
    df = pd.DataFrame(file_data)
    
    # Sort by full path for better organization
    df = df.sort_values('full_path').reset_index(drop=True)
    
    # Generate output filename if not provided
    if output_file is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        directory_name = Path(directory_path).name
        output_file = f"file_inventory_{directory_name}_{timestamp}.csv"
    
    # Save to CSV
    df.to_csv(output_file, index=False)
    print(f"💾 File inventory saved to: {output_file}")
    
    # Display summary statistics
    if include_stats:
        print_summary_stats(df)
    
    return df

def print_summary_stats(df):
    """Print summary statistics about the file inventory."""
    print(f"\n📊 INVENTORY SUMMARY")
    print(f"=" * 50)
    
    # Basic counts
    total_files = len(df)
    total_size = df['size_bytes'].sum()
    total_dirs = df['directory'].nunique()
    
    print(f"Total files: {total_files:,}")
    print(f"Total directories: {total_dirs:,}")
    print(f"Total size: {format_size(total_size)}")
    
    # File type breakdown
    print(f"\n📁 File Types (Top 10):")
    file_type_counts = df['file_type'].value_counts().head(10)
    for file_type, count in file_type_counts.items():
        percentage = (count / total_files) * 100
        print(f"  {file_type:<12} {count:>6,} files ({percentage:>5.1f}%)")
    
    # Size breakdown by file type
    print(f"\n💾 Storage by File Type (Top 10):")
    size_by_type = df.groupby('file_type')['size_bytes'].sum().sort_values(ascending=False).head(10)
    for file_type, size in size_by_type.items():
        percentage = (size / total_size) * 100
        print(f"  {file_type:<12} {format_size(size):>10} ({percentage:>5.1f}%)")
    
    # Largest files
    print(f"\n🔍 Largest Files (Top 10):")
    largest_files = df.nlargest(10, 'size_bytes')[['filename', 'size_human', 'file_type']]
    for idx, row in largest_files.iterrows():
        print(f"  {row['filename']:<40} {row['size_human']:>10} ({row['file_type']})")
    
    # Most recent files
    print(f"\n📅 Most Recently Modified (Top 5):")
    try:
        df['modified_datetime'] = pd.to_datetime(df['modified_date'], format='mixed')
        recent_files = df.nlargest(5, 'modified_datetime')[['filename', 'modified_date']]
        for idx, row in recent_files.iterrows():
            # Format the date nicely
            mod_date = pd.to_datetime(row['modified_date'], format='mixed').strftime('%Y-%m-%d %H:%M:%S')
            print(f"  {row['filename']:<40} {mod_date}")
    except Exception as e:
        print(f"  (Date formatting error: {e})")
        # Fallback to showing raw dates
        recent_files = df.nlargest(5, 'modified_date')[['filename', 'modified_date']]
        for idx, row in recent_files.iterrows():
            print(f"  {row['filename']:<40} {row['modified_date']}")

def main():
    """Main function to run the file inventory generator."""
    parser = argparse.ArgumentParser(
        description="Generate a comprehensive file inventory CSV",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python file_inventory.py                              # Scan current directory
  python file_inventory.py --directory /path/to/scan    # Scan specific directory
  python file_inventory.py --output my_files.csv        # Custom output filename
  python file_inventory.py --no-stats                   # Skip summary statistics
        """
    )
    
    parser.add_argument(
        '--directory',
        default='.',
        help='Directory to scan (default: current directory)'
    )
    
    parser.add_argument(
        '--output',
        help='Output CSV filename (auto-generated if not provided)'
    )
    
    parser.add_argument(
        '--no-stats',
        action='store_true',
        help='Skip printing summary statistics'
    )
    
    parser.add_argument(
        '--include-hidden',
        action='store_true',
        help='Include hidden directories like .git, .venv, etc.'
    )
    
    args = parser.parse_args()
    
    # Validate directory
    if not os.path.exists(args.directory):
        print(f"❌ Error: Directory not found: {args.directory}")
        return 1
    
    if not os.path.isdir(args.directory):
        print(f"❌ Error: Path is not a directory: {args.directory}")
        return 1
    
    print(f"🚀 Starting file inventory generation")
    print(f"Directory: {os.path.abspath(args.directory)}")
    print(f"Include hidden: {args.include_hidden}")
    print()
    
    try:
        # Create the inventory
        df = create_file_inventory(
            directory_path=args.directory,
            output_file=args.output,
            include_stats=not args.no_stats
        )
        
        if df is not None:
            print(f"\n✅ File inventory completed successfully!")
            return 0
        else:
            print(f"\n❌ File inventory failed - no files found")
            return 1
            
    except KeyboardInterrupt:
        print(f"\n🛑 Operation interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())