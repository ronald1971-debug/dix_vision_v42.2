import os
from pathlib import Path

def enumerate_all_files(root_dir):
    """Enumerate all files in the directory tree."""
    all_files = []
    root_path = Path(root_dir)
    
    for file_path in root_path.rglob('*'):
        if file_path.is_file():
            all_files.append(str(file_path))
    
    return all_files

if __name__ == "__main__":
    files = enumerate_all_files("C:/dix_vision_v42.2")
    print(f"Total files: {len(files)}")
    
    with open("complete_file_index.txt", "w") as f:
        for i, file_path in enumerate(files, 1):
            f.write(f"{i},{file_path}\n")
    
    print("File index saved to complete_file_index.txt")