import os
from pathlib import Path

def enumerate_source_files(root_dir):
    """Enumerate Python source files in key directories."""
    key_dirs = [
        "cognitive_engine",
        "intelligence_engine", 
        "learning_engine",
        "sensory",
        "evolution_engine",
        "knowledge_engine",
        "reasoning_engine",
        "self_model",
        "world_model",
        "simulation_engine",
        "trader_modeling",
        "mission_system",
        "governance",
        "governance_engine",
        "runtime",
        "execution",
        "mind",
        "enforcement",
        "state",
        "translation",
        "system"
    ]
    
    source_files = []
    root_path = Path(root_dir)
    
    for dir_name in key_dirs:
        dir_path = root_path / dir_name
        if dir_path.exists():
            for file_path in dir_path.rglob('*.py'):
                if file_path.is_file():
                    source_files.append(str(file_path))
    
    return source_files

if __name__ == "__main__":
    files = enumerate_source_files("C:/dix_vision_v42.2")
    print(f"Total source Python files: {len(files)}")
    
    with open("C:/dix_vision_v42.2/source_file_index.txt", "w") as f:
        for i, file_path in enumerate(files, 1):
            relative_path = file_path.replace("C:\\dix_vision_v42.2\\", "")
            f.write(f"{i},{relative_path}\n")
    
    print("Source file index saved")