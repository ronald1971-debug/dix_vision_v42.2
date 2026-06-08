#!/usr/bin/env python3
"""
Generate comprehensive file index for dixvision-v42.2 system analysis
"""
import json
import os
from collections import defaultdict
from pathlib import Path


def generate_file_index(root_dir):
    """Generate complete file index with unique IDs"""
    root_path = Path(root_dir)
    file_index = []
    dir_stats = defaultdict(int)
    type_stats = defaultdict(int)
    unreadable = []
    
    # Walk through all files
    for root, dirs, files in os.walk(root_path):
        for file in files:
            file_path = Path(root) / file
            relative_path = file_path.relative_to(root_path)
            
            try:
                # Get file info
                file_size = file_path.stat().st_size
                file_ext = file_path.suffix.lower()
                
                # Determine file type
                if file_ext in ['.py']:
                    file_type = 'Python'
                elif file_ext in ['.js', '.jsx', '.ts', '.tsx']:
                    file_type = 'JavaScript/TypeScript'
                elif file_ext in ['.html', '.htm']:
                    file_type = 'HTML'
                elif file_ext in ['.css']:
                    file_type = 'CSS'
                elif file_ext in ['.md']:
                    file_type = 'Markdown'
                elif file_ext in ['.json']:
                    file_type = 'JSON'
                elif file_ext in ['.yaml', '.yml']:
                    file_type = 'YAML'
                elif file_ext in ['.proto']:
                    file_type = 'Proto'
                elif file_ext in ['.dart']:
                    file_type = 'Dart'
                elif file_ext in ['.rs']:
                    file_type = 'Rust'
                elif file_ext in ['.txt']:
                    file_type = 'Text'
                elif file_ext in ['.log']:
                    file_type = 'Log'
                elif file_ext in ['.zip', '.tar', '.gz']:
                    file_type = 'Archive'
                elif file_ext in ['.lnk']:
                    file_type = 'Shortcut'
                else:
                    file_type = 'Other'
                
                # Get parent directory
                parent_dir = str(relative_path.parent)
                
                # Update stats
                dir_stats[parent_dir] += 1
                type_stats[file_type] += 1
                
                file_index.append({
                    'path': str(relative_path),
                    'absolute_path': str(file_path),
                    'type': file_type,
                    'size': file_size,
                    'directory': parent_dir
                })
                
            except Exception as e:
                unreadable.append({
                    'path': str(relative_path),
                    'error': str(e)
                })
    
    # Assign IDs
    for idx, file_info in enumerate(file_index, 1):
        file_info['id'] = f"ID_{idx:04d}"
    
    return {
        'total_files': len(file_index),
        'file_index': file_index,
        'directory_stats': dict(dir_stats),
        'type_stats': dict(type_stats),
        'unreadable_files': unreadable
    }

if __name__ == '__main__':
    root_dir = r'C:\dix_vision_v42.2'
    index_data = generate_file_index(root_dir)
    
    # Save to JSON
    output_file = r'C:\dix_vision_v42.2\SYSTEM_FILE_INDEX.json'
    with open(output_file, 'w') as f:
        json.dump(index_data, f, indent=2)
    
    # Print summary
    print(f"TOTAL FILES: {index_data['total_files']}")
    print("\nFILE TYPE STATS:")
    for file_type, count in sorted(index_data['type_stats'].items()):
        print(f"  {file_type}: {count}")
    
    print("\nTOP 20 DIRECTORIES BY FILE COUNT:")
    sorted_dirs = sorted(index_data['directory_stats'].items(), key=lambda x: x[1], reverse=True)[:20]
    for dir_name, count in sorted_dirs:
        print(f"  {dir_name}: {count} files")
    
    if index_data['unreadable_files']:
        print(f"\nUNREADABLE FILES: {len(index_data['unreadable_files'])}")
        for file_info in index_data['unreadable_files']:
            print(f"  {file_info['path']}: {file_info['error']}")
    
    print(f"\nFile index saved to: {output_file}")
