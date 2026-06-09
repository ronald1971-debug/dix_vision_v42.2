#!/usr/bin/env python3
"""
Documentation Fix Script - Archive Historical Documents
Creates archive directories and moves outdated documentation
"""

import os
import shutil
from pathlib import Path

def create_archive_directories():
    """Create archive directories for historical documents."""
    base_path = Path("C:/dix_vision_v42.2")
    
    archive_dirs = [
        "archived_phase_reports",
        "archived_fix_reports", 
        "archived_migration",
        "archived_outdated"
    ]
    
    for dir_name in archive_dirs:
        archive_path = base_path / dir_name
        archive_path.mkdir(exist_ok=True)
        print(f"Created directory: {archive_path}")

def move_phase_reports():
    """Move historical phase reports to archive."""
    base_path = Path("C:/dix_vision_v42.2")
    archive_path = base_path / "archived_phase_reports"
    
    phase_reports = [
        "PHASE1_COMPLETION_REPORT.md",
        "PHASE1_PROGRESS_REPORT.md", 
        "PHASE2.1_COMPLETE_REPORT.md",
        "PHASE2_COMPLETE_FINAL.md",
        "PHASE2_EXECUTION_CONSOLIDATION.md",
        "PHASE2_EXECUTION_PROGRESS.md",
        "PHASE2_INTEGRATION_VERIFICATION.md",
        "PHASE2_STATUS_UPDATE.md",
        "PHASE3_COMPLETE.md",
        "PHASE8_ASSESSMENT.md",
        "PHASE8_FINAL_REPORT.md",
        "PHASE9_ASSESSMENT.md",
        "PHASE9_FINAL_REPORT.md",
        "PHASE10_ASSESSMENT.md",
        "PHASE10_FINAL_REPORT.md",
        "PHASE11.1_ASSESSMENT.md",
        "PHASE11.1_FINAL_REPORT.md",
        "PHASE11.1_IMPLEMENTATION_FINAL_REPORT.md",
        "PHASE11_ASSESSMENT.md",
        "PHASE11_FINAL_REPORT.md",
        "PHASE12_ASSESSMENT.md",
        "PHASE12_FINAL_REPORT.md",
        "PHASE13_ASSESSMENT.md",
        "PHASE13_FINAL_REPORT.md"
    ]
    
    moved_count = 0
    for report in phase_reports:
        source = base_path / report
        if source.exists():
            destination = archive_path / report
            shutil.move(str(source), str(destination))
            print(f"Moved: {report} → archived_phase_reports/")
            moved_count += 1
    
    print(f"\nMoved {moved_count} phase reports to archive")

def move_fix_reports():
    """Move temporary fix reports to archive."""
    base_path = Path("C:/dix_vision_v42.2")
    archive_path = base_path / "archived_fix_reports"
    
    fix_reports = [
        "FILE_ENCODING_FIXED.md",
        "RUNTIME_WARNINGS_FIXED.md", 
        "SYNTAX_ERROR_FIXED.md",
        "WORKAROUND_APPLIED.md",
        "LOCKS_REMOVED.md"
    ]
    
    moved_count = 0
    for report in fix_reports:
        source = base_path / report
        if source.exists():
            destination = archive_path / report
            shutil.move(str(source), str(destination))
            print(f"Moved: {report} → archived_fix_reports/")
            moved_count += 1
    
    print(f"\nMoved {moved_count} fix reports to archive")

def move_migration_reports():
    """Move migration artifacts to archive."""
    base_path = Path("C:/dix_vision_v42.2")
    archive_path = base_path / "archived_migration"
    
    migration_reports = [
        "IMPORT_MIGRATION_BLOCKED.md",
        "IMPORT_MIGRATION_COMPLETE.md",
        "IMPORT_MIGRATION_PLAN.md",
        "IMPORT_MIGRATION_READY.md"
    ]
    
    moved_count = 0
    for report in migration_reports:
        source = base_path / report
        if source.exists():
            destination = archive_path / report
            shutil.move(str(source), str(destination))
            print(f"Moved: {report} → archived_migration/")
            moved_count += 1
    
    print(f"\nMoved {moved_count} migration reports to archive")

def move_outdated_reports():
    """Move outdated analysis reports to archive."""
    base_path = Path("C:/dix_vision_v42.2")
    archive_path = base_path / "archived_outdated"
    
    outdated_reports = [
        "FINAL_SYSTEM_ANALYSIS_REPORT.md",  # Superseded by comprehensive
        "SYSTEM_ANALYSIS_TRACKING.md",      # Historical tracking
        "SYSTEM_COMPREHENSIVE_ANALYSIS.md",  # Duplicate
        "ORPHAN_FILE_ANALYSIS.md",          # Historical analysis
        "MIND_CONTROL_INTEGRATION_SUMMARY.md" # Superseded by full integration
    ]
    
    moved_count = 0
    for report in outdated_reports:
        source = base_path / report
        if source.exists():
            destination = archive_path / report
            shutil.move(str(source), str(destination))
            print(f"Moved: {report} → archived_outdated/")
            moved_count += 1
    
    print(f"\nMoved {moved_count} outdated reports to archive")

def remove_outdated_status_files():
    """Remove clearly outdated status files."""
    base_path = Path("C:/dix_vision_v42.2")
    
    outdated_status = [
        "BUILD_PLAN_STATUS.md",
        "PLUGIN_STATUS.md",
        "TEST_LINT_STATUS.md",
        "SERVER_OPERATIONAL.md", 
        "SYSTEM_OPERATIONAL.md",
        "SESSION_LOG.md"
    ]
    
    removed_count = 0
    for status_file in outdated_status:
        source = base_path / status_file
        if source.exists():
            source.unlink()
            print(f"Removed: {status_file}")
            removed_count += 1
    
    print(f"\nRemoved {removed_count} outdated status files")

if __name__ == "__main__":
    print("=== DOCUMENTATION FIX SCRIPT ===\n")
    
    print("Creating archive directories...")
    create_archive_directories()
    
    print("\nMoving historical phase reports...")
    move_phase_reports()
    
    print("\nMoving temporary fix reports...")
    move_fix_reports()
    
    print("\nMoving migration artifacts...")
    move_migration_reports()
    
    print("\nMoving outdated analysis reports...")
    move_outdated_reports()
    
    print("\nRemoving outdated status files...")
    remove_outdated_status_files()
    
    print("\n=== DOCUMENTATION FIX COMPLETE ===")
    print("Historical documents archived, core documentation streamlined")