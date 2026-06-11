import os
import csv
from pathlib import Path

def build_file_index():
    base_path = Path(r'C:\dix_vision_v42.2')
    output_file = Path(r'C:\dix_vision_v42.2\full_system_file_index.csv')
    
    files_data = []
    file_id = 1
    
    # Walk through all files
    for root, dirs, files in os.walk(base_path):
        # Skip hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            file_path = Path(root) / file
            relative_path = file_path.relative_to(base_path)
            
            # Get file info
            try:
                size = file_path.stat().st_size
                file_ext = file_path.suffix.lower() if file_path.suffix else 'no_extension'
                directory = str(relative_path.parent)
                
                files_data.append({
                    'file_id': file_id,
                    'file_path': str(relative_path),
                    'full_path': str(file_path),
                    'directory': directory if directory != '.' else 'root',
                    'file_type': file_ext,
                    'size_bytes': size
                })
                file_id += 1
            except Exception as e:
                print(f"Error accessing {file_path}: {e}")
    
    # Write to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['file_id', 'file_path', 'full_path', 'directory', 'file_type', 'size_bytes'])
        writer.writeheader()
        writer.writerows(files_data)
    
    print(f"Total files found: {len(files_data)}")
    print(f"Index written to: {output_file}")
    
    # Print summary by directory
    print("\n--- Directory Summary ---")
    dir_counts = {}
    for item in files_data:
        dir_name = item['directory']
        dir_counts[dir_name] = dir_counts.get(dir_name, 0) + 1
    
    for dir_name, count in sorted(dir_counts.items()):
        print(f"{dir_name}: {count} files")
    
    return files_data

if __name__ == "__main__":
    build_file_index()
