#!/usr/bin/env python3
"""
Safe Duplicate File Cleanup Script

This script identifies and safely removes duplicate files based on name and size.
It includes safety features like dry-run mode, backups, and user confirmation.

FEATURES:
- Dry-run mode to preview changes
- Backup creation before deletion
- Smart preservation rules
- Interactive confirmation
- Detailed logging
- Recovery capabilities

USAGE:
    python cleanup_duplicates.py --dry-run          # Preview changes
    python cleanup_duplicates.py --backup           # Create backups
    python cleanup_duplicates.py --confirm          # Actually delete files
"""

import os
import sys
import shutil
import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict

class DuplicateCleanup:
    def __init__(self, workspace_dir, dry_run=True, create_backup=False):
        self.workspace_dir = Path(workspace_dir)
        self.dry_run = dry_run
        self.create_backup = create_backup
        self.backup_dir = self.workspace_dir / "backup_before_cleanup"
        self.log_file = self.workspace_dir / f"cleanup_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Directories to preserve (keep all copies)
        self.preserve_dirs = {
            '.git',
            '.venv',
            'node_modules',
            '__pycache__',
            '.pytest_cache'
        }
        
        # File patterns to be extra careful with
        self.critical_files = {
            'README.md',
            'package.json',
            'requirements.txt',
            '.gitignore',
            'LICENSE',
            'Makefile'
        }
        
        # Rules for which copy to keep (priority order)
        self.preservation_rules = [
            lambda path: not any(preserve in str(path) for preserve in self.preserve_dirs),  # Not in preserve dirs
            lambda path: len(str(path).split(os.sep)) < 10,  # Shorter path (closer to root)
            lambda path: "Schedule & Logistics" not in str(path),  # Not in the duplicate structure
            lambda path: not str(path).startswith("."),  # Not hidden
            lambda path: "original" in str(path).lower(),  # Contains "original"
            lambda path: "backup" not in str(path).lower(),  # Doesn't contain "backup"
        ]
        
        self.stats = {
            'files_analyzed': 0,
            'duplicate_groups': 0,
            'files_to_delete': 0,
            'space_to_save': 0,
            'files_preserved': 0,
            'errors': []
        }
        
        self.actions = []  # Log of all actions taken

    def get_file_info(self, file_path):
        """Get comprehensive file information."""
        try:
            stat_info = os.stat(file_path)
            return {
                'path': str(file_path),
                'name': os.path.basename(file_path),
                'size': stat_info.st_size,
                'modified': stat_info.st_mtime,
                'created': stat_info.st_ctime
            }
        except (OSError, IOError) as e:
            self.stats['errors'].append(f"Error accessing {file_path}: {e}")
            return None

    def should_preserve_directory(self, path):
        """Check if directory should be preserved entirely."""
        path_str = str(path)
        return any(preserve_dir in path_str for preserve_dir in self.preserve_dirs)

    def is_critical_file(self, filename):
        """Check if file is critical and should be handled carefully."""
        return filename in self.critical_files

    def select_file_to_keep(self, file_list):
        """
        Select which file to keep from a list of duplicates.
        Uses preservation rules to make intelligent decisions.
        """
        if len(file_list) <= 1:
            return file_list[0] if file_list else None
        
        # Sort files by preservation rules
        scored_files = []
        for file_info in file_list:
            score = 0
            path = Path(file_info['path'])
            
            # Apply preservation rules (higher score = better to keep)
            for i, rule in enumerate(self.preservation_rules):
                if rule(path):
                    score += len(self.preservation_rules) - i
            
            # Bonus for older files (original might be older)
            score += (datetime.now().timestamp() - file_info['modified']) / 86400 / 365  # Years old
            
            scored_files.append((score, file_info))
        
        # Sort by score (highest first) and return the best file to keep
        scored_files.sort(key=lambda x: x[0], reverse=True)
        return scored_files[0][1]

    def find_duplicates(self):
        """Find all duplicate files in the workspace."""
        print(f"🔍 Scanning for duplicates in: {self.workspace_dir}")
        
        file_groups = defaultdict(list)
        
        for root, dirs, files in os.walk(self.workspace_dir):
            # Skip preserved directories
            dirs[:] = [d for d in dirs if not any(preserve in d for preserve in self.preserve_dirs)]
            
            for file in files:
                file_path = os.path.join(root, file)
                file_info = self.get_file_info(file_path)
                
                if file_info:
                    self.stats['files_analyzed'] += 1
                    key = (file_info['name'], file_info['size'])
                    file_groups[key].append(file_info)
        
        # Filter to only groups with duplicates
        duplicates = {key: files for key, files in file_groups.items() if len(files) > 1}
        self.stats['duplicate_groups'] = len(duplicates)
        
        return duplicates

    def plan_cleanup(self, duplicates):
        """Plan which files to delete and which to keep."""
        cleanup_plan = []
        
        for (filename, size), file_list in duplicates.items():
            # Skip critical files - require manual review
            if self.is_critical_file(filename):
                print(f"⚠️  SKIPPING critical file: {filename} (requires manual review)")
                self.stats['files_preserved'] += len(file_list) - 1
                continue
            
            # Select file to keep
            file_to_keep = self.select_file_to_keep(file_list)
            files_to_delete = [f for f in file_list if f['path'] != file_to_keep['path']]
            
            if files_to_delete:
                cleanup_plan.append({
                    'filename': filename,
                    'size': size,
                    'keep': file_to_keep,
                    'delete': files_to_delete,
                    'space_saved': size * len(files_to_delete)
                })
                
                self.stats['files_to_delete'] += len(files_to_delete)
                self.stats['space_to_save'] += size * len(files_to_delete)
        
        return cleanup_plan

    def create_backup(self, file_path):
        """Create a backup of a file before deletion."""
        if not self.create_backup:
            return True
        
        try:
            # Create backup directory if it doesn't exist
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Preserve directory structure in backup
            rel_path = Path(file_path).relative_to(self.workspace_dir)
            backup_path = self.backup_dir / rel_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(file_path, backup_path)
            return True
            
        except Exception as e:
            self.stats['errors'].append(f"Backup failed for {file_path}: {e}")
            return False

    def format_size(self, size_bytes):
        """Convert bytes to human readable format."""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"

    def preview_cleanup(self, cleanup_plan):
        """Show preview of what will be cleaned up."""
        print(f"\n📋 CLEANUP PREVIEW")
        print(f"=" * 50)
        
        if not cleanup_plan:
            print("✅ No duplicates found that can be safely cleaned!")
            return
        
        print(f"📊 Summary:")
        print(f"  • Files to be deleted: {self.stats['files_to_delete']}")
        print(f"  • Space to be saved: {self.format_size(self.stats['space_to_save'])}")
        print(f"  • Duplicate groups: {len(cleanup_plan)}")
        
        print(f"\n🗂️  Top 10 space savers:")
        sorted_plan = sorted(cleanup_plan, key=lambda x: x['space_saved'], reverse=True)
        
        for i, item in enumerate(sorted_plan[:10], 1):
            print(f"  {i:2d}. {item['filename']} ({self.format_size(item['space_saved'])})")
            print(f"      KEEP: {item['keep']['path']}")
            for file_to_delete in item['delete']:
                print(f"      DELETE: {file_to_delete['path']}")
            print()

    def execute_cleanup(self, cleanup_plan):
        """Execute the cleanup plan."""
        if self.dry_run:
            print("🔍 DRY RUN MODE - No files will be deleted")
            return True
        
        print(f"\n🧹 EXECUTING CLEANUP")
        print(f"=" * 50)
        
        success_count = 0
        
        for item in cleanup_plan:
            for file_to_delete in item['delete']:
                file_path = file_to_delete['path']
                
                try:
                    # Create backup if requested
                    if self.create_backup:
                        if not self.create_backup(file_path):
                            print(f"❌ Skipping {file_path} - backup failed")
                            continue
                    
                    # Delete the file
                    os.remove(file_path)
                    success_count += 1
                    
                    # Log the action
                    action = {
                        'action': 'delete',
                        'file': file_path,
                        'size': file_to_delete['size'],
                        'timestamp': datetime.now().isoformat(),
                        'kept_copy': item['keep']['path']
                    }
                    self.actions.append(action)
                    
                    print(f"✅ Deleted: {file_path}")
                    
                except Exception as e:
                    error_msg = f"Failed to delete {file_path}: {e}"
                    self.stats['errors'].append(error_msg)
                    print(f"❌ {error_msg}")
        
        print(f"\n📊 Cleanup completed: {success_count} files deleted")
        return success_count > 0

    def save_log(self):
        """Save detailed log of all actions."""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'workspace': str(self.workspace_dir),
            'dry_run': self.dry_run,
            'backup_created': self.create_backup,
            'backup_location': str(self.backup_dir) if self.create_backup else None,
            'stats': self.stats,
            'actions': self.actions
        }
        
        try:
            with open(self.log_file, 'w') as f:
                json.dump(log_data, f, indent=2)
            print(f"📝 Log saved to: {self.log_file}")
        except Exception as e:
            print(f"❌ Failed to save log: {e}")

    def run(self):
        """Main execution function."""
        print(f"🚀 Starting duplicate cleanup")
        print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE'}")
        print(f"Backup: {'Enabled' if self.create_backup else 'Disabled'}")
        print()
        
        # Find duplicates
        duplicates = self.find_duplicates()
        
        if not duplicates:
            print("✅ No duplicate files found!")
            return
        
        # Plan cleanup
        cleanup_plan = self.plan_cleanup(duplicates)
        
        # Show preview
        self.preview_cleanup(cleanup_plan)
        
        # Execute if not dry run
        if cleanup_plan:
            if not self.dry_run:
                response = input(f"\n❓ Proceed with cleanup? (y/N): ").strip().lower()
                if response != 'y':
                    print("🛑 Cleanup cancelled by user")
                    return
            
            self.execute_cleanup(cleanup_plan)
        
        # Save log
        self.save_log()
        
        # Show final stats
        print(f"\n📊 FINAL STATISTICS")
        print(f"=" * 50)
        print(f"Files analyzed: {self.stats['files_analyzed']}")
        print(f"Duplicate groups found: {self.stats['duplicate_groups']}")
        print(f"Files marked for deletion: {self.stats['files_to_delete']}")
        print(f"Potential space savings: {self.format_size(self.stats['space_to_save'])}")
        if self.stats['errors']:
            print(f"Errors encountered: {len(self.stats['errors'])}")


def main():
    parser = argparse.ArgumentParser(
        description="Safely remove duplicate files from workspace",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cleanup_duplicates.py --dry-run              # Preview what would be deleted
  python cleanup_duplicates.py --backup --confirm     # Create backups and delete
  python cleanup_duplicates.py --confirm              # Delete without backups
        """
    )
    
    parser.add_argument(
        '--dry-run', 
        action='store_true', 
        default=True,
        help='Preview changes without deleting files (default)'
    )
    
    parser.add_argument(
        '--confirm', 
        action='store_true',
        help='Actually delete files (overrides --dry-run)'
    )
    
    parser.add_argument(
        '--backup', 
        action='store_true',
        help='Create backups before deleting files'
    )
    
    parser.add_argument(
        '--workspace',
        default="/Users/venkateshtadinada/Documents/VS-Code-Projects/folder-kb",
        help='Workspace directory to clean (default: current workspace)'
    )
    
    args = parser.parse_args()
    
    # Determine if this is a dry run
    dry_run = not args.confirm
    
    if not os.path.exists(args.workspace):
        print(f"❌ Error: Workspace directory not found: {args.workspace}")
        sys.exit(1)
    
    # Create and run cleanup
    cleanup = DuplicateCleanup(
        workspace_dir=args.workspace,
        dry_run=dry_run,
        create_backup=args.backup
    )
    
    try:
        cleanup.run()
    except KeyboardInterrupt:
        print(f"\n🛑 Cleanup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()