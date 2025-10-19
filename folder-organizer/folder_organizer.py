#!/usr/bin/env python3
"""
Folder Organizer Script
Automatically organize files into folders based on file types, dates, or custom rules.
"""

import os
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Callable
import logging
import json
from colorama import init, Fore, Style
from tqdm import tqdm

# Initialize colorama for cross-platform colored output
init()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FolderOrganizer:
    # Default file type categories
    DEFAULT_CATEGORIES = {
        'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg', '.ico', '.heic'],
        'Documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.pages'],
        'Spreadsheets': ['.xls', '.xlsx', '.csv', '.ods', '.numbers'],
        'Presentations': ['.ppt', '.pptx', '.odp', '.key'],
        'Videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v'],
        'Audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a'],
        'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz'],
        'Code': ['.py', '.js', '.html', '.css', '.cpp', '.java', '.php', '.rb', '.go', '.rs'],
        'Executables': ['.exe', '.msi', '.deb', '.rpm', '.dmg', '.pkg', '.app'],
        'Fonts': ['.ttf', '.otf', '.woff', '.woff2', '.eot']
    }
    
    def __init__(self, source_dir: str, target_dir: Optional[str] = None, 
                 dry_run: bool = True, copy_files: bool = False):
        self.source_dir = Path(source_dir)
        self.target_dir = Path(target_dir) if target_dir else self.source_dir
        self.dry_run = dry_run
        self.copy_files = copy_files
        self.moved_files = []
        self.failed_files = []
        
        if not self.source_dir.exists():
            raise FileNotFoundError(f"Source directory {source_dir} does not exist")
    
    def get_files(self, recursive: bool = False, include_hidden: bool = False) -> List[Path]:
        """Get all files from the source directory."""
        files = []
        pattern = "**/*" if recursive else "*"
        
        for item in self.source_dir.glob(pattern):
            if item.is_file():
                # Skip hidden files unless requested
                if not include_hidden and item.name.startswith('.'):
                    continue
                files.append(item)
        
        return sorted(files)
    
    def organize_by_type(self, categories: Optional[Dict[str, List[str]]] = None, 
                        recursive: bool = False, include_hidden: bool = False) -> Dict[str, int]:
        """Organize files by their type/extension."""
        if categories is None:
            categories = self.DEFAULT_CATEGORIES
        
        files = self.get_files(recursive, include_hidden)
        stats = {}
        
        print(f"{Fore.CYAN}Organizing {len(files)} files by type...{Style.RESET_ALL}")
        
        for file_path in tqdm(files, desc="Organizing", unit="file"):
            file_ext = file_path.suffix.lower()
            
            # Find matching category
            target_folder = "Others"
            for category, extensions in categories.items():
                if file_ext in extensions:
                    target_folder = category
                    break
            
            # Move file to appropriate folder
            if self._move_file(file_path, target_folder):
                stats[target_folder] = stats.get(target_folder, 0) + 1
        
        return stats
    
    def organize_by_date(self, date_format: str = "%Y-%m", 
                        use_creation_date: bool = False,
                        recursive: bool = False, include_hidden: bool = False) -> Dict[str, int]:
        """Organize files by their modification or creation date."""
        files = self.get_files(recursive, include_hidden)
        stats = {}
        
        print(f"{Fore.CYAN}Organizing {len(files)} files by date...{Style.RESET_ALL}")
        
        for file_path in tqdm(files, desc="Organizing", unit="file"):
            try:
                # Get file date
                if use_creation_date:
                    timestamp = file_path.stat().st_ctime
                else:
                    timestamp = file_path.stat().st_mtime
                
                file_date = datetime.fromtimestamp(timestamp)
                folder_name = file_date.strftime(date_format)
                
                # Move file to date folder
                if self._move_file(file_path, folder_name):
                    stats[folder_name] = stats.get(folder_name, 0) + 1
                    
            except Exception as e:
                logger.error(f"Failed to get date for {file_path.name}: {e}")
                self.failed_files.append(str(file_path))
        
        return stats
    
    def organize_by_size(self, size_ranges: Optional[Dict[str, tuple]] = None,
                        recursive: bool = False, include_hidden: bool = False) -> Dict[str, int]:
        """Organize files by their size."""
        if size_ranges is None:
            size_ranges = {
                'Small (< 1MB)': (0, 1024*1024),
                'Medium (1-10MB)': (1024*1024, 10*1024*1024),
                'Large (10-100MB)': (10*1024*1024, 100*1024*1024),
                'Very Large (> 100MB)': (100*1024*1024, float('inf'))
            }
        
        files = self.get_files(recursive, include_hidden)
        stats = {}
        
        print(f"{Fore.CYAN}Organizing {len(files)} files by size...{Style.RESET_ALL}")
        
        for file_path in tqdm(files, desc="Organizing", unit="file"):
            try:
                file_size = file_path.stat().st_size
                
                # Find matching size range
                target_folder = "Unknown Size"
                for range_name, (min_size, max_size) in size_ranges.items():
                    if min_size <= file_size < max_size:
                        target_folder = range_name
                        break
                
                # Move file to size folder
                if self._move_file(file_path, target_folder):
                    stats[target_folder] = stats.get(target_folder, 0) + 1
                    
            except Exception as e:
                logger.error(f"Failed to get size for {file_path.name}: {e}")
                self.failed_files.append(str(file_path))
        
        return stats
    
    def organize_by_name_pattern(self, patterns: Dict[str, str],
                               recursive: bool = False, include_hidden: bool = False) -> Dict[str, int]:
        """Organize files based on filename patterns."""
        files = self.get_files(recursive, include_hidden)
        stats = {}
        
        print(f"{Fore.CYAN}Organizing {len(files)} files by name patterns...{Style.RESET_ALL}")
        
        for file_path in tqdm(files, desc="Organizing", unit="file"):
            filename = file_path.name.lower()
            
            # Find matching pattern
            target_folder = "Others"
            for folder_name, pattern in patterns.items():
                if pattern.lower() in filename:
                    target_folder = folder_name
                    break
            
            # Move file to pattern folder
            if self._move_file(file_path, target_folder):
                stats[target_folder] = stats.get(target_folder, 0) + 1
        
        return stats
    
    def organize_by_custom_rules(self, rules_file: str,
                               recursive: bool = False, include_hidden: bool = False) -> Dict[str, int]:
        """Organize files using custom rules from a JSON file."""
        with open(rules_file, 'r', encoding='utf-8') as f:
            rules = json.load(f)
        
        files = self.get_files(recursive, include_hidden)
        stats = {}
        
        print(f"{Fore.CYAN}Organizing {len(files)} files using custom rules...{Style.RESET_ALL}")
        
        for file_path in tqdm(files, desc="Organizing", unit="file"):
            target_folder = self._apply_custom_rules(file_path, rules)
            
            if self._move_file(file_path, target_folder):
                stats[target_folder] = stats.get(target_folder, 0) + 1
        
        return stats
    
    def _apply_custom_rules(self, file_path: Path, rules: Dict) -> str:
        """Apply custom rules to determine target folder."""
        filename = file_path.name.lower()
        file_ext = file_path.suffix.lower()
        file_size = file_path.stat().st_size
        
        # Check each rule
        for rule in rules.get('rules', []):
            conditions = rule.get('conditions', {})
            folder = rule.get('folder', 'Others')
            
            match = True
            
            # Check extension condition
            if 'extensions' in conditions:
                if file_ext not in conditions['extensions']:
                    match = False
            
            # Check name pattern condition
            if 'name_contains' in conditions and match:
                if conditions['name_contains'].lower() not in filename:
                    match = False
            
            # Check size condition
            if 'size_range' in conditions and match:
                min_size, max_size = conditions['size_range']
                if not (min_size <= file_size <= max_size):
                    match = False
            
            if match:
                return folder
        
        return rules.get('default_folder', 'Others')
    
    def _move_file(self, source_path: Path, target_folder: str) -> bool:
        """Move or copy a file to the target folder."""
        try:
            # Create target directory
            target_dir = self.target_dir / target_folder
            
            if not self.dry_run:
                target_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate target file path
            target_path = target_dir / source_path.name
            
            # Handle name conflicts
            counter = 1
            original_target = target_path
            while target_path.exists() and not self.dry_run:
                stem = original_target.stem
                suffix = original_target.suffix
                target_path = target_dir / f"{stem}_{counter}{suffix}"
                counter += 1
            
            if self.dry_run:
                logger.info(f"Would move: {source_path} → {target_path}")
            else:
                if self.copy_files:
                    shutil.copy2(source_path, target_path)
                    logger.info(f"Copied: {source_path.name} → {target_folder}/")
                else:
                    shutil.move(str(source_path), str(target_path))
                    logger.info(f"Moved: {source_path.name} → {target_folder}/")
                
                self.moved_files.append(str(target_path))
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to move {source_path.name}: {e}")
            self.failed_files.append(str(source_path))
            return False
    
    def create_undo_script(self, output_file: str = "undo_organization.py"):
        """Create a script to undo the organization."""
        if not self.moved_files:
            print(f"{Fore.YELLOW}No files were moved, no undo script needed{Style.RESET_ALL}")
            return
        
        undo_script = f'''#!/usr/bin/env python3
"""
Auto-generated undo script for folder organization
Run this script to move files back to their original locations
"""

import shutil
from pathlib import Path

def undo_organization():
    moved_files = {self.moved_files}
    source_dir = Path("{self.source_dir}")
    
    success_count = 0
    for file_path in moved_files:
        try:
            file_path = Path(file_path)
            if file_path.exists():
                target_path = source_dir / file_path.name
                
                # Handle name conflicts
                counter = 1
                original_target = target_path
                while target_path.exists():
                    stem = original_target.stem
                    suffix = original_target.suffix
                    target_path = source_dir / f"{{stem}}_{{counter}}{{suffix}}"
                    counter += 1
                
                shutil.move(str(file_path), str(target_path))
                print(f"Moved back: {{file_path.name}}")
                success_count += 1
            else:
                print(f"File not found: {{file_path}}")
        except Exception as e:
            print(f"Failed to move {{file_path}}: {{e}}")
    
    print(f"Successfully moved back {{success_count}} files")

if __name__ == "__main__":
    undo_organization()
'''
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(undo_script)
        
        print(f"{Fore.GREEN}Undo script created: {output_file}{Style.RESET_ALL}")
    
    def get_stats(self) -> Dict[str, int]:
        """Get organization statistics."""
        return {
            'moved_files': len(self.moved_files),
            'failed_files': len(self.failed_files)
        }

def create_sample_rules(output_file: str):
    """Create a sample custom rules file."""
    sample_rules = {
        "description": "Sample custom organization rules",
        "default_folder": "Others",
        "rules": [
            {
                "name": "Work Documents",
                "folder": "Work",
                "conditions": {
                    "extensions": [".docx", ".xlsx", ".pptx"],
                    "name_contains": "work"
                }
            },
            {
                "name": "Screenshots",
                "folder": "Screenshots",
                "conditions": {
                    "extensions": [".png", ".jpg"],
                    "name_contains": "screenshot"
                }
            },
            {
                "name": "Large Videos",
                "folder": "Large Videos",
                "conditions": {
                    "extensions": [".mp4", ".avi", ".mkv"],
                    "size_range": [100*1024*1024, float('inf')]
                }
            },
            {
                "name": "Project Files",
                "folder": "Projects",
                "conditions": {
                    "extensions": [".py", ".js", ".html", ".css"]
                }
            }
        ]
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(sample_rules, f, indent=2)
    
    print(f"{Fore.GREEN}Sample rules file created: {output_file}{Style.RESET_ALL}")

def main():
    parser = argparse.ArgumentParser(description="Folder Organizer")
    parser.add_argument("source_dir", help="Source directory to organize")
    parser.add_argument("--target-dir", help="Target directory (default: same as source)")
    
    # Organization methods
    parser.add_argument("--by-type", action="store_true", help="Organize by file type")
    parser.add_argument("--by-date", action="store_true", help="Organize by date")
    parser.add_argument("--by-size", action="store_true", help="Organize by file size")
    parser.add_argument("--by-name", help="Organize by name patterns (JSON string)")
    parser.add_argument("--custom-rules", help="Use custom rules from JSON file")
    
    # Options
    parser.add_argument("--date-format", default="%Y-%m", 
                       help="Date format for date organization (default: %%Y-%%m)")
    parser.add_argument("--use-creation-date", action="store_true",
                       help="Use creation date instead of modification date")
    parser.add_argument("--recursive", action="store_true",
                       help="Process files in subdirectories")
    parser.add_argument("--include-hidden", action="store_true",
                       help="Include hidden files")
    parser.add_argument("--copy", action="store_true",
                       help="Copy files instead of moving them")
    parser.add_argument("--execute", action="store_true",
                       help="Execute organization (default is dry run)")
    parser.add_argument("--create-undo", action="store_true",
                       help="Create undo script after organization")
    
    # Utilities
    parser.add_argument("--create-sample-rules", help="Create sample custom rules file")
    
    args = parser.parse_args()
    
    if args.create_sample_rules:
        create_sample_rules(args.create_sample_rules)
        return
    
    try:
        organizer = FolderOrganizer(
            args.source_dir, 
            args.target_dir, 
            dry_run=not args.execute,
            copy_files=args.copy
        )
        
        stats = {}
        
        # Determine organization method
        if args.by_type:
            stats = organizer.organize_by_type(
                recursive=args.recursive, 
                include_hidden=args.include_hidden
            )
        elif args.by_date:
            stats = organizer.organize_by_date(
                args.date_format,
                args.use_creation_date,
                args.recursive,
                args.include_hidden
            )
        elif args.by_size:
            stats = organizer.organize_by_size(
                recursive=args.recursive,
                include_hidden=args.include_hidden
            )
        elif args.by_name:
            patterns = json.loads(args.by_name)
            stats = organizer.organize_by_name_pattern(
                patterns,
                args.recursive,
                args.include_hidden
            )
        elif args.custom_rules:
            stats = organizer.organize_by_custom_rules(
                args.custom_rules,
                args.recursive,
                args.include_hidden
            )
        else:
            print(f"{Fore.RED}No organization method specified. Use --help for options.{Style.RESET_ALL}")
            return
        
        # Show results
        print(f"\n{Fore.CYAN}Organization Results:{Style.RESET_ALL}")
        for folder, count in stats.items():
            print(f"  {folder}: {count} files")
        
        org_stats = organizer.get_stats()
        if org_stats['failed_files'] > 0:
            print(f"\n{Fore.YELLOW}Failed to organize {org_stats['failed_files']} files{Style.RESET_ALL}")
        
        if not args.execute:
            print(f"\n{Fore.YELLOW}DRY RUN - Use --execute to perform actual organization{Style.RESET_ALL}")
        elif args.create_undo:
            organizer.create_undo_script()
    
    except Exception as e:
        logger.error(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
