"""
InfraNest Cleanup Script
Removes stale files, old ZIPs, cache, and ensures system integrity
Run this before each build or periodically to maintain clean state
"""

import os
import sys
import json
import hashlib
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set

# ANSI color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def log_info(msg: str) -> None:
    """Log info message"""
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")

def log_success(msg: str) -> None:
    """Log success message"""
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def log_warning(msg: str) -> None:
    """Log warning message"""
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")

def log_error(msg: str) -> None:
    """Log error message"""
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def log_header(msg: str) -> None:
    """Log header message"""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{msg}{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}\n")

def calculate_file_hash(file_path: Path) -> str:
    """Calculate SHA256 hash of a file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def clean_pycache(root_dir: Path) -> int:
    """Remove all __pycache__ directories"""
    log_info("Cleaning Python cache directories...")
    count = 0
    for pycache_dir in root_dir.rglob('__pycache__'):
        try:
            shutil.rmtree(pycache_dir)
            count += 1
            log_success(f"Removed: {pycache_dir.relative_to(root_dir)}")
        except Exception as e:
            log_error(f"Failed to remove {pycache_dir}: {e}")
    return count

def clean_old_zips(root_dir: Path) -> int:
    """Remove old ZIP files from generated projects"""
    log_info("Cleaning old ZIP files...")
    count = 0
    for zip_file in root_dir.rglob('*.zip'):
        # Skip template zips
        if 'templates' not in str(zip_file):
            try:
                zip_file.unlink()
                count += 1
                log_success(f"Removed: {zip_file.relative_to(root_dir)}")
            except Exception as e:
                log_error(f"Failed to remove {zip_file}: {e}")
    return count

def clean_temp_files(root_dir: Path) -> int:
    """Remove temporary files"""
    log_info("Cleaning temporary files...")
    count = 0
    patterns = ['*.pyc', '*.pyo', '*.tmp', '*~', '.DS_Store']
    
    for pattern in patterns:
        for temp_file in root_dir.rglob(pattern):
            try:
                temp_file.unlink()
                count += 1
                log_success(f"Removed: {temp_file.relative_to(root_dir)}")
            except Exception as e:
                log_error(f"Failed to remove {temp_file}: {e}")
    return count

def find_redundant_entry_files(core_dir: Path) -> List[Path]:
    """Find redundant entry point files (keeping only server.py)"""
    log_info("Checking for redundant entry files...")
    
    # CANONICAL entry point
    canonical_entry = 'server.py'
    
    # Potential redundant entry files
    potential_redundant = [
        'app.py',           # Old entry point
        'run_server.py',    # Duplicate entry
        'start.py',         # Alternative entry
        'main.py',          # Generic entry
    ]
    
    redundant_files = []
    for filename in potential_redundant:
        file_path = core_dir / filename
        if file_path.exists():
            redundant_files.append(file_path)
            log_warning(f"Found redundant entry: {filename} (canonical: {canonical_entry})")
    
    return redundant_files

def archive_redundant_files(files: List[Path], archive_dir: Path) -> int:
    """Archive redundant files instead of deleting"""
    if not files:
        return 0
    
    log_info(f"Archiving {len(files)} redundant files...")
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    # Create timestamped archive subdirectory
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    archive_subdir = archive_dir / f"archive_{timestamp}"
    archive_subdir.mkdir(exist_ok=True)
    
    count = 0
    for file_path in files:
        try:
            dest = archive_subdir / file_path.name
            shutil.move(str(file_path), str(dest))
            count += 1
            log_success(f"Archived: {file_path.name} → {archive_subdir.name}/")
        except Exception as e:
            log_error(f"Failed to archive {file_path.name}: {e}")
    
    return count

def update_integrity_file(core_dir: Path) -> None:
    """Update integrity.json with current file checksums"""
    log_info("Updating integrity.json...")
    
    integrity_data: Dict[str, str] = {}
    
    # Key files to track
    key_files = [
        'server.py',
        'app_clean.py',
        'parsers/dsl_parser.py',
        'generators/base_generator.py',
        'generators/django_generator.py',
        'generators/go_generator.py',
        'generators/rails_generator.py',
        'ai_providers/simple_ai_manager.py',
        'ai_providers/groq_provider.py',
    ]
    
    for file_rel_path in key_files:
        file_path = core_dir / file_rel_path
        if file_path.exists():
            file_hash = calculate_file_hash(file_path)
            integrity_data[file_rel_path] = file_hash
            log_success(f"Tracked: {file_rel_path} ({file_hash[:8]}...)")
        else:
            log_warning(f"Missing: {file_rel_path}")
    
    # Save integrity file
    integrity_file = core_dir / 'integrity.json'
    with open(integrity_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'files': integrity_data,
            'canonical_entry': 'server.py'
        }, f, indent=2)
    
    log_success(f"Integrity file updated: {len(integrity_data)} files tracked")

def verify_single_entry_point(core_dir: Path) -> bool:
    """Verify only server.py exists as entry point"""
    log_info("Verifying single entry point enforcement...")
    
    server_py = core_dir / 'server.py'
    if not server_py.exists():
        log_error("Canonical entry point 'server.py' not found!")
        return False
    
    # Check for any other potential entry files
    other_entries = find_redundant_entry_files(core_dir)
    
    if not other_entries:
        log_success("✅ Single entry point verified: server.py")
        return True
    else:
        log_warning(f"Found {len(other_entries)} redundant entry files")
        return False

def main():
    """Main cleanup routine"""
    log_header("🧹 InfraNest Cleanup Utility")
    
    # Get project root
    core_dir = Path(__file__).parent.absolute()
    project_root = core_dir.parent
    
    log_info(f"Core directory: {core_dir}")
    log_info(f"Project root: {project_root}")
    
    total_removed = 0
    
    # 1. Clean Python cache
    log_header("Step 1: Python Cache")
    total_removed += clean_pycache(project_root)
    
    # 2. Clean old ZIPs
    log_header("Step 2: Old ZIP Files")
    total_removed += clean_old_zips(project_root)
    
    # 3. Clean temporary files
    log_header("Step 3: Temporary Files")
    total_removed += clean_temp_files(project_root)
    
    # 4. Handle redundant entry files
    log_header("Step 4: Redundant Entry Files")
    redundant_files = find_redundant_entry_files(core_dir)
    
    if redundant_files:
        print(f"\n{Colors.YELLOW}Found {len(redundant_files)} redundant entry files:{Colors.END}")
        for f in redundant_files:
            print(f"  • {f.name}")
        
        response = input(f"\n{Colors.BOLD}Archive these files? (y/N): {Colors.END}").strip().lower()
        
        if response == 'y':
            archive_dir = core_dir / '_archived'
            archived_count = archive_redundant_files(redundant_files, archive_dir)
            log_success(f"Archived {archived_count} files to {archive_dir}")
        else:
            log_info("Skipped archiving redundant files")
    else:
        log_success("No redundant entry files found")
    
    # 5. Update integrity file
    log_header("Step 5: Integrity Tracking")
    update_integrity_file(core_dir)
    
    # 6. Verify single entry point
    log_header("Step 6: Entry Point Verification")
    verify_single_entry_point(core_dir)
    
    # Summary
    log_header("✨ Cleanup Summary")
    log_success(f"Total files removed: {total_removed}")
    log_success("System cleanup complete!")
    log_info("You can now run the backend with: python core/server.py")
    print()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Cleanup cancelled by user{Colors.END}")
        sys.exit(0)
    except Exception as e:
        log_error(f"Cleanup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
