"""
COCKPIT DIRECTORY CLEANUP - PARTIAL REMOVAL STRATEGY

Date: 2026-06-11
Status: Backend services migrated, preserving launcher/widgets for now

MIGRATED AND READY FOR REMOVAL (Backend Services):
- auth.py → cognitive_control_center/shared_services/auth.py ✅
- chat.py → cognitive_control_center/shared_services/chat.py ✅
- llm.py → cognitive_control_center/shared_services/llm.py ✅
- qr.py → cognitive_control_center/shared_services/qr.py ✅
- pairing.py → cognitive_control_center/shared_services/pairing.py ✅

PRESERVE FOR NOW (Not Yet Migrated):
- launcher.py - Desktop launcher, needs cognitive_control_center migration
- widgets/ - UI widgets, will be integrated in Dashboard2026 transformation
- static/ - Legacy HTML frontend, being replaced by cognitive environment
- api/ - API endpoints, need migration to cognitive_control_center
- audit/ - Audit trail components, need migration
- cli/ - CLI integration, need migration
- mobile/ - Mobile client components, need migration
- app.py - Standalone FastAPI shim (backward compatibility)
- operator_ide.py - Operator IDE, needs migration
- voice_alerts.py - Voice alerts, needs migration
- charter.py - Charter management, already exists in core/

STRATEGY:
- Remove migrated backend files to prevent confusion
- Preserve launcher, widgets, static for continued functionality
- Update DEPRECATED.md to reflect partial removal status
- Document remaining migration tasks for future phases
"""

import sys
import shutil
from pathlib import Path

def remove_migrated_backend_services():
    """Remove backend service files that have been migrated to cognitive_control_center"""
    
    cockpit_dir = Path("c:/dix_vision_v42.2/cockpit")
    
    # Files that have been migrated and can be safely removed
    migrated_files = [
        "auth.py",
        "chat.py", 
        "llm.py",
        "qr.py",
        "pairing.py",
    ]
    
    removed_files = []
    for filename in migrated_files:
        filepath = cockpit_dir / filename
        if filepath.exists():
            # Create backup first
            backup_path = cockpit_dir / f"{filename}.backup"
            shutil.copy(filepath, backup_path)
            # Remove original
            filepath.unlink()
            removed_files.append(filename)
            print(f"[REMOVED] {filename} (backup: {filename}.backup)")
        else:
            print(f"[SKIP] {filename} not found")
    
    return removed_files

def update_deprecated_status():
    """Update DEPRECATED.md to reflect partial removal"""
    
    deprecated_file = Path("c:/dix_vision_v42.2/cockpit/DEPRECATED.md")
    
    if not deprecated_file.exists():
        print("[SKIP] DEPRECATED.md not found")
        return
    
    # Read current content
    with open(deprecated_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Add note about partial removal
    removal_note = """
## Backend Service Removal (2026-06-11)

The following backend services have been migrated to cognitive_control_center/ and removed:
- auth.py → cognitive_control_center/shared_services/auth.py
- chat.py → cognitive_control_center/shared_services/chat.py  
- llm.py → cognitive_control_center/shared_services/llm.py
- qr.py → cognitive_control_center/shared_services/qr.py
- pairing.py → cognitive_control_center/shared_services/pairing.py

Backups exist as *.backup files for rollback if needed.

Remaining components (launcher, widgets, static, api) are preserved for continued
functionality and will be migrated in future phases.
"""
    
    new_content = content + removal_note
    
    with open(deprecated_file, "w", encoding="utf-8") as f:
        f.write(new_content)
    
    print(f"[UPDATED] DEPRECATED.md with removal status")

if __name__ == "__main__":
    print("=" * 70)
    print("COCKPIT DIRECTORY PARTIAL CLEANUP")
    print("=" * 70)
    
    try:
        removed = remove_migrated_backend_services()
        print(f"\n[SUCCESS] Removed {len(removed)} migrated backend service files")
        print("[INFO] Backups created as *.backup files")
        
        update_deprecated_status()
        print("\n[INFO] DEPRECATED.md updated")
        
        print("\n" + "=" * 70)
        print("PRESERVED (Not Removed):")
        print("=" * 70)
        print("- launcher.py (desktop launcher)")
        print("- widgets/ (UI widgets - will migrate with Dashboard2026)")
        print("- static/ (HTML frontend - being replaced)")
        print("- api/ (API endpoints - future migration)")
        print("- audit/, cli/, mobile/ (remaining components)")
        
    except Exception as e:
        print(f"\n[ERROR] Cleanup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
