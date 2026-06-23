#!/usr/bin/env python
"""
Archived Session Deletion Tool for DIX VISION
Helps manage and delete archived sessions that may be causing OOM errors
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("delete_sessions")


class ArchivedSessionManager:
    """Manage and delete archived sessions"""

    def __init__(self):
        self.session_locations = [
            "containers/development/checkpoints",
            "containers/system_core/state",
            ".devin/sessions",
            "AppData/Local/Windsurf/sessions",  # Windows location
            "AppData/Roaming/Code/User/Storage"   # VS Code location
        ]

    def find_session_files(self):
        """Find all session-related files"""
        session_files = []

        # Check project directories
        project_sessions = [
            "containers/development/checkpoints",
            "containers/system_core/state"
        ]

        for location in project_sessions:
            path = Path(location)
            if path.exists():
                for file in path.rglob("*"):
                    if file.is_file():
                        session_files.append({
                            'path': str(file),
                            'size_mb': file.stat().st_size / (1024 * 1024),
                            'modified': datetime.fromtimestamp(file.stat().st_mtime),
                            'type': 'checkpoint' if 'checkpoint' in str(file) else 'state'
                        })

        # Check common IDE session locations
        ide_locations = [
            Path.home() / "AppData/Local/Windsurf",
            Path.home() / "AppData/Roaming/Code/User/Storage",
            Path.home() / ".config/Windsurf",
            Path.home() / ".config/Code/User/Storage"
        ]

        for location in ide_locations:
            if location.exists():
                for file in location.rglob("*"):
                    if file.is_file() and any(x in str(file).lower() for x in ['session', 'state', 'backup']):
                        session_files.append({
                            'path': str(file),
                            'size_mb': file.stat().st_size / (1024 * 1024),
                            'modified': datetime.fromtimestamp(file.stat().st_mtime),
                            'type': 'ide_session'
                        })

        return session_files

    def list_sessions(self):
        """List all found sessions"""
        sessions = self.find_session_files()

        print(f"=== Found {len(sessions)} session-related files ===")
        print()

        if not sessions:
            print("No session files found")
            return

        # Group by type
        by_type = {}
        for session in sessions:
            stype = session['type']
            if stype not in by_type:
                by_type[stype] = []
            by_type[stype].append(session)

        for stype, files in by_type.items():
            print(f"\n{stype.upper()} FILES ({len(files)}):")
            for file in files[-5:]:  # Show last 5 files
                print(f"  {Path(file['path']).name}")
                print(f"    Size: {file['size_mb']:.2f} MB")
                print(f"    Modified: {file['modified']}")
                print(f"    Path: {file['path']}")

    def delete_session_by_pattern(self, pattern):
        """Delete sessions matching a pattern"""
        sessions = self.find_session_files()
        deleted = []

        for session in sessions:
            if pattern.lower() in Path(session['path']).name.lower():
                try:
                    path = Path(session['path'])
                    if path.is_file():
                        path.unlink()
                        deleted.append(str(path))
                    elif path.is_dir():
                        shutil.rmtree(path)
                        deleted.append(str(path))
                    logger.info(f"Deleted: {path}")
                except Exception as e:
                    logger.error(f"Failed to delete {path}: {e}")

        return deleted

    def delete_old_sessions(self, days_old=7):
        """Delete sessions older than specified days"""
        sessions = self.find_session_files()
        cutoff_date = datetime.now() - timedelta(days=days_old)
        deleted = []

        for session in sessions:
            if session['modified'] < cutoff_date:
                try:
                    path = Path(session['path'])
                    if path.is_file():
                        path.unlink()
                        deleted.append(str(path))
                    elif path.is_dir():
                        shutil.rmtree(path)
                        deleted.append(str(path))
                    logger.info(f"Deleted old session: {path}")
                except Exception as e:
                    logger.error(f"Failed to delete {path}: {e}")

        return deleted

    def delete_large_sessions(self, size_mb_threshold=10):
        """Delete sessions larger than threshold"""
        sessions = self.find_session_files()
        deleted = []

        for session in sessions:
            if session['size_mb'] > size_mb_threshold:
                try:
                    path = Path(session['path'])
                    if path.is_file():
                        path.unlink()
                        deleted.append(str(path))
                    elif path.is_dir():
                        shutil.rmtree(path)
                        deleted.append(str(path))
                    logger.info(f"Deleted large session: {path} ({session['size_mb']:.2f} MB)")
                except Exception as e:
                    logger.error(f"Failed to delete {path}: {e}")

        return deleted

    def interactive_delete(self):
        """Interactive session deletion"""
        sessions = self.find_session_files()

        if not sessions:
            print("No session files found")
            return

        print(f"=== Interactive Session Deletion ===")
        print(f"Found {len(sessions)} session-related files")
        print()

        for i, session in enumerate(sessions, 1):
            print(f"{i}. {Path(session['path']).name}")
            print(f"   Size: {session['size_mb']:.2f} MB")
            print(f"   Modified: {session['modified']}")
            print(f"   Path: {session['path']}")
            print()

        try:
            choice = input("Enter numbers to delete (comma-separated, or 'all' for all): ")

            if choice.lower() == 'all':
                for session in sessions:
                    try:
                        Path(session['path']).unlink()
                        print(f"Deleted: {Path(session['path']).name}")
                    except Exception as e:
                        print(f"Failed: {e}")
            else:
                indices = [int(x.strip()) for x in choice.split(',')]
                for idx in indices:
                    if 1 <= idx <= len(sessions):
                        try:
                            Path(sessions[idx-1]['path']).unlink()
                            print(f"Deleted: {Path(sessions[idx-1]['path']).name}")
                        except Exception as e:
                            print(f"Failed: {e}")

        except KeyboardInterrupt:
            print("\nDeletion cancelled")
        except Exception as e:
            print(f"Error: {e}")


def main():
    """Main execution"""
    manager = ArchivedSessionManager()

    print("=== Archived Session Manager ===")
    print()

    print("1. List all sessions")
    print("2. Delete by pattern")
    print("3. Delete old sessions (older than 7 days)")
    print("4. Delete large sessions (>10 MB)")
    print("5. Interactive deletion")

    try:
        choice = input("Choose option (1-5): ")

        if choice == '1':
            manager.list_sessions()
        elif choice == '2':
            pattern = input("Enter pattern to match: ")
            deleted = manager.delete_session_by_pattern(pattern)
            print(f"Deleted {len(deleted)} files")
        elif choice == '3':
            days = input("Enter days threshold (default 7): ")
            days = int(days) if days else 7
            deleted = manager.delete_old_sessions(days)
            print(f"Deleted {len(deleted)} files")
        elif choice == '4':
            size = input("Enter size threshold in MB (default 10): ")
            size = int(size) if size else 10
            deleted = manager.delete_large_sessions(size)
            print(f"Deleted {len(deleted)} files")
        elif choice == '5':
            manager.interactive_delete()
        else:
            print("Invalid choice")

    except KeyboardInterrupt:
        print("\nOperation cancelled")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()