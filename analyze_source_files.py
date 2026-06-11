import csv
from pathlib import Path

def filter_source_files():
    input_file = Path(r'C:\dix_vision_v42.2\full_system_file_index.csv')
    output_file = Path(r'C:\dix_vision_v42.2\source_files_index.csv')
    
    # File types to include
    source_extensions = {
        '.py', '.js', '.ts', '.tsx', '.jsx', '.rs', '.go', '.java', '.cpp', '.c', '.h',
        '.yaml', '.yml', '.json', '.toml', '.md', '.txt', '.sh', '.bat', '.ps1',
        '.proto', '.sql'
    }
    
    # Directories to exclude
    exclude_dirs = {
        'node_modules', '__pycache__', '.git', '.next', 'dist', 'build',
        'target', 'venv', 'env', '.venv', 'site-packages', 'eggs'
    }
    
    source_files = []
    file_id = 1
    
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Check if directory should be excluded
            directory = row['directory']
            should_exclude = any(exclude_dir in directory for exclude_dir in exclude_dirs)
            
            # Check if file type should be included
            file_ext = row['file_type']
            is_source = file_ext in source_extensions or file_ext == 'no_extension'
            
            # Also include important root files even if no extension
            if directory == 'root' and not should_exclude:
                is_source = True
            
            if not should_exclude and is_source:
                source_files.append({
                    'file_id': file_id,
                    'file_path': row['file_path'],
                    'full_path': row['full_path'],
                    'directory': row['directory'],
                    'file_type': row['file_type'],
                    'size_bytes': row['size_bytes']
                })
                file_id += 1
    
    # Write filtered index
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['file_id', 'file_path', 'full_path', 'directory', 'file_type', 'size_bytes'])
        writer.writeheader()
        writer.writerows(source_files)
    
    print(f"Total source files found: {len(source_files)}")
    print(f"Filtered from: {40539} total files")
    print(f"Source file index written to: {output_file}")
    
    # Print summary by directory
    print("\n--- Source File Directory Summary ---")
    dir_counts = {}
    type_counts = {}
    
    for item in source_files:
        dir_name = item['directory']
        file_type = item['file_type']
        dir_counts[dir_name] = dir_counts.get(dir_name, 0) + 1
        type_counts[file_type] = type_counts.get(file_type, 0) + 1
    
    print("\nBy Directory (top 20):")
    for dir_name, count in sorted(dir_counts.items(), key=lambda x: x[1], reverse=True)[:20]:
        print(f"  {dir_name}: {count} files")
    
    print("\nBy File Type:")
    for file_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {file_type}: {count} files")
    
    return source_files

if __name__ == "__main__":
    filter_source_files()
