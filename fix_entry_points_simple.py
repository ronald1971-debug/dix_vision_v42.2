import os
import glob

# Fix entry point scripts
entry_files = glob.glob('containers/github_repos/*/entry_point.sh')
print(f"Found {len(entry_files)} entry point files")

for file_path in entry_files:
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix the Python import statement
    if 'python3 -c "' in content and 'sys.path.append' not in content:
        old_import_start = 'python3 -c "\n'
        new_import_start = '''python3 -c "
import sys
sys.path.append('/app')
sys.path.append('/app/governance')
sys.path.append('/app/adapters')

'''
        content = content.replace(old_import_start, new_import_start)
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"Fixed {file_path}")

print("Entry point fixes complete")
