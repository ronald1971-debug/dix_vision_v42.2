#!/usr/bin/env python3
"""
Comprehensive OOM Diagnosis Tool
Analyzes system to find the real cause of OOM errors
"""
import os
import sys
import subprocess
import json
from pathlib import Path

def check_large_files():
    """Find files that might cause memory issues when loaded"""
    large_files = []
    search_dirs = [
        ".",
        "containers",
        "containers/development",
        "containers/system_core"
    ]
    
    for directory in search_dirs:
        if os.path.exists(directory):
            for root, dirs, files in os.walk(directory):
                for file in files:
                    try:
                        file_path = os.path.join(root, file)
                        file_size = os.path.getsize(file_path)
                        if file_size > 10 * 1024 * 1024:  # > 10MB
                            large_files.append({
                                'path': file_path,
                                'size_mb': file_size / (1024 * 1024)
                            })
                    except (OSError, PermissionError):
                        pass
    
    return large_files

def check_docker_memory():
    """Check Docker container memory usage"""
    try:
        result = subprocess.run(
            ['docker', 'stats', '--no-stream', '--format', 'json'],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            containers = json.loads(result.stdout)
            return containers
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        pass
    return []

def check_process_memory():
    """Check memory usage of potentially problematic processes"""
    try:
        result = subprocess.run(
            ['powershell', '-Command', 
             'Get-Process | Where-Object {$_.ProcessName -like \"*Devin*\" -or $_.ProcessName -like \"*node*\" -or $_.ProcessName -like \"*python*\"} | Select-Object ProcessName, Id, @{Name=\"MemoryMB\";Expression={[math]::Round($_.WorkingSet/1MB,2)}} | ConvertTo-Json'],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            processes = json.loads(result.stdout)
            return processes
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        pass
    return []

def check_ide_logs():
    """Check recent IDE error logs"""
    log_paths = [
        "C:\\Users\\prive\\OneDrive\\Desktop\\errrrrrr.txt",
        "C:\\Users\\prive\\AppData\\Roaming\\Devin\\logs\\*.log",
        "C:\\Users\\prive\\AppData\\Local\\Devin\\logs\\*.log"
    ]
    
    recent_errors = []
    for log_pattern in log_paths:
        if os.path.exists(log_pattern.replace("*", "")):
            try:
                with open(log_pattern.replace("*", ""), 'r') as f:
                    content = f.read()
                    if 'OOM' in content or 'out of memory' in content.lower():
                        recent_errors.append(log_pattern)
            except (OSError, PermissionError):
                pass
    
    return recent_errors

def main():
    print("=" * 50)
    print("COMPREHENSIVE OOM DIAGNOSIS")
    print("=" * 50)
    
    # Check for large files
    print("\n1. Checking for large files (>10MB)...")
    large_files = check_large_files()
    if large_files:
        print(f"Found {len(large_files)} large files:")
        for file in sorted(large_files, key=lambda x: x['size_mb'], reverse=True)[:10]:
            print(f"  {file['path']}: {file['size_mb']:.2f} MB")
    else:
        print("No large files found")
    
    # Check Docker memory
    print("\n2. Checking Docker container memory...")
    containers = check_docker_memory()
    if containers:
        print(f"Docker containers running: {len(containers)}")
        for container in containers[:5]:
            print(f"  {container.get('Name', 'unknown')}: {container.get('MemUsage', 'unknown')}")
    else:
        print("No Docker containers or unable to get stats")
    
    # Check process memory
    print("\n3. Checking process memory usage...")
    processes = check_process_memory()
    if processes:
        print("High memory processes:")
        for proc in sorted(processes, key=lambda x: x.get('MemoryMB', 0), reverse=True)[:10]:
            print(f"  {proc.get('ProcessName', 'unknown')} (PID {proc.get('Id', 'unknown')}): {proc.get('MemoryMB', 0)} MB")
    else:
        print("Unable to get process information")
    
    # Check IDE logs
    print("\n4. Checking IDE logs for OOM errors...")
    error_logs = check_ide_logs()
    if error_logs:
        print(f"Found OOM errors in: {error_logs}")
    else:
        print("No OOM errors found in logs")
    
    print("\n" + "=" * 50)
    print("DIAGNOSIS COMPLETE")
    print("=" * 50)

if __name__ == "__main__":
    main()