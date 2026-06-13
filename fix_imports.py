import os
import glob

# Fix governance wrapper imports
governance_files = glob.glob('containers/github_repos/*//*_governance_wrapper.py')
print(f"Found {len(governance_files)} governance wrapper files")

for file_path in governance_files:
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix the import statement
    if 'from base_external_repo_wrapper import' in content and 'sys.path.append' not in content:
        old_import = 'from base_external_repo_wrapper import'
        new_import = '''import sys
import os
sys.path.append('/app/governance')

from base_external_repo_wrapper import'''
        content = content.replace(old_import, new_import)
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"Fixed {file_path}")

# Fix domain adapter imports
adapter_files = glob.glob('containers/github_repos/*//*_domain_adapter.py')
print(f"Found {len(adapter_files)} domain adapter files")

for file_path in adapter_files:
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix the import statement
    if 'from base_domain_adapter import' in content and 'sys.path.append' not in content:
        old_import = 'from base_domain_adapter import'
        new_import = '''import sys
import os
sys.path.append('/app/adapters')

from base_domain_adapter import'''
        content = content.replace(old_import, new_import)
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"Fixed {file_path}")

print("Import path fixes complete")
