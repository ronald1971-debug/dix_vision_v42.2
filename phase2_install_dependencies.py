#!/usr/bin/env python3
"""
DIX VISION - Phase 2 Dependency Integration Script
Installs all 90+ external library wrappers from github_repos/
"""

import subprocess
import sys
import time
from pathlib import Path

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

def print_success(text):
    print(f"{GREEN}[OK] {text}{RESET}")

def print_error(text):
    print(f"{RED}[FAIL] {text}{RESET}")

def print_warning(text):
    print(f"{YELLOW}[WARN] {text}{RESET}")

def install_package(package):
    """Install a single package using pip"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package],
            capture_output=True,
            text=True,
            timeout=300
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False
    except Exception as e:
        print_error(f"Exception installing {package}: {e}")
        return False

def main():
    print_header("DIX VISION Phase 2 - Dependency Integration")
    
    # Path to requirements
    requirements_path = Path("C:/dix_vision_v42.2/requirements_enhanced.txt")
    
    if not requirements_path.exists():
        print_error(f"Requirements file not found: {requirements_path}")
        sys.exit(1)
    
    # Read requirements
    with open(requirements_path, 'r') as f:
        lines = f.readlines()
    
    # Filter out comments and empty lines, extract package names
    packages = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            # Extract package name (before >= or ==)
            package = line.split('>=')[0].split('==')[0].split('<')[0].strip()
            if package:
                packages.append(package)
    
    print_success(f"Found {len(packages)} packages to install")
    print_warning("This may take several minutes...")
    
    # Install packages
    successful = []
    failed = []
    skipped = []
    
    for i, package in enumerate(packages, 1):
        print(f"[{i}/{len(packages)}] Installing {package}...", end=" ")
        
        # Check if already installed
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "show", package],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                print_success(f"Already installed")
                skipped.append(package)
                continue
        except:
            pass
        
        # Install package
        if install_package(package):
            print_success(f"Installed successfully")
            successful.append(package)
        else:
            print_error(f"Installation failed")
            failed.append(package)
        
        # Small delay to prevent rate limiting
        time.sleep(0.1)
    
    # Summary
    print_header("Installation Summary")
    print_success(f"Successfully installed: {len(successful)}")
    print_warning(f"Already installed: {len(skipped)}")
    print_error(f"Failed to install: {len(failed)}")
    
    if failed:
        print("\nFailed packages:")
        for package in failed:
            print_error(f"  - {package}")
    
    print("\nTotal packages processed:", len(packages))
    print("Success rate:", f"{100 * (len(successful) + len(skipped)) / len(packages):.1f}%")
    
    # Write report
    report_path = Path("C:/dix_vision_v42.2/phase2_installation_report.txt")
    with open(report_path, 'w') as f:
        f.write("DIX VISION Phase 2 - Installation Report\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Total packages: {len(packages)}\n")
        f.write(f"Successfully installed: {len(successful)}\n")
        f.write(f"Already installed: {len(skipped)}\n")
        f.write(f"Failed: {len(failed)}\n")
        f.write(f"Success rate: {100 * (len(successful) + len(skipped)) / len(packages):.1f}%\n\n")
        
        if failed:
            f.write("\nFailed packages:\n")
            for package in failed:
                f.write(f"  - {package}\n")
    
    print_success(f"\nReport saved to: {report_path}")
    
    return 0 if not failed else 1

if __name__ == "__main__":
    sys.exit(main())
