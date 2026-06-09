#!/usr/bin/env python3
"""
System Analysis Tracking Table Generator for DIX VISION v42.2
Generates comprehensive tracking table for 100% file coverage analysis
"""

import csv
from pathlib import Path
from collections import defaultdict

def generate_tracking_table():
    """Generate tracking table from complete file list"""
    
    base_path = Path("C:/dix_vision_v42.2")
    file_list_path = base_path / "complete_file_list.txt"
    
    # Read file list
    with open(file_list_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Parse file paths (skip header)
    files = []
    for line in lines[3:]:  # Skip header lines
        line = line.strip()
        if line and not line.startswith('-') and line.startswith('C:\\'):
            files.append(line)
    
    # Create tracking table structure
    tracking_data = []
    
    # Group files by directory for analysis
    dir_groups = defaultdict(list)
    for file_path in files:
        path_obj = Path(file_path)
        rel_path = path_obj.relative_to(base_path)
        parent_dir = str(rel_path.parent).replace('\\', '/')
        dir_groups[parent_dir].append(str(rel_path))
    
    # Assign file IDs and categorize importance
    file_id = 1
    critical_patterns = [
        'main.py', 'bootstrap_kernel.py', 'governance/kernel.py', 
        'governance/charter.py', 'runtime/convergence.py',
        'execution/engine.py', 'mind/engine.py',
        'enforcement/runtime_guardian.py', 'translation/validator.py'
    ]
    
    high_importance_dirs = [
        'governance', 'cognitive_engine', 'execution', 'enforcement',
        'translation', 'runtime', 'state', 'indira', 'dyon', 'system',
        'observability', 'security'
    ]
    
    for parent_dir, file_list in sorted(dir_groups.items()):
        for file_path in sorted(file_list):
            # Determine importance
            importance = "medium"
            file_name = Path(file_path).name
            
            if any(pattern in file_path for pattern in critical_patterns):
                importance = "critical"
            elif any(dir_name in parent_dir for dir_name in high_importance_dirs):
                importance = "high"
            elif file_path.endswith('.md') and 'PHASE' in file_name:
                importance = "high"  # Analysis reports
            
            # Determine file type
            file_ext = Path(file_path).suffix
            if file_ext == '.py':
                file_type = "Python"
            elif file_ext in ['.ts', '.tsx']:
                file_type = "TypeScript"
            elif file_ext == '.md':
                file_type = "Markdown"
            elif file_ext in ['.yaml', '.yml']:
                file_type = "YAML"
            elif file_ext == '.json':
                file_type = "JSON"
            elif file_ext == '.proto':
                file_type = "Protobuf"
            elif file_ext == '.lean':
                file_type = "Lean"
            elif file_ext == '.rs':
                file_type = "Rust"
            else:
                file_type = "Other"
            
            tracking_data.append({
                'file_id': f"F{file_id:04d}",
                'file_path': file_path,
                'directory': parent_dir,
                'file_type': file_type,
                'importance': importance,
                'status': 'pending',
                'analyzed': 'no',
                'summary': '',
                'issues': '',
                'production_ready': ''
            })
            file_id += 1
    
    # Write tracking table
    output_path = base_path / "analysis_tracking_table.csv"
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'file_id', 'file_path', 'directory', 'file_type', 'importance',
            'status', 'analyzed', 'summary', 'issues', 'production_ready'
        ])
        writer.writeheader()
        writer.writerows(tracking_data)
    
    print(f"Generated tracking table with {len(tracking_data)} files")
    print(f"Output: {output_path}")
    
    # Print summary statistics
    importance_counts = defaultdict(int)
    type_counts = defaultdict(int)
    for item in tracking_data:
        importance_counts[item['importance']] += 1
        type_counts[item['file_type']] += 1
    
    print("\n=== IMPORTANCE DISTRIBUTION ===")
    for imp, count in sorted(importance_counts.items()):
        print(f"{imp}: {count}")
    
    print("\n=== FILE TYPE DISTRIBUTION ===")
    for ftype, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"{ftype}: {count}")
    
    return tracking_data

if __name__ == "__main__":
    generate_tracking_table()