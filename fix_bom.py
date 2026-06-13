import yaml

# Read the compose.yaml file and remove BOM
with open('compose.yaml', 'rb') as f:
    content = f.read()

# Remove BOM if present
if content.startswith(b'\xef\xbb\xbf'):
    content = content[3:]
    print('Removed BOM from compose.yaml')
    
    with open('compose.yaml', 'wb') as f:
        f.write(content)
else:
    print('No BOM found in compose.yaml')

# Validate YAML
with open('compose.yaml', 'r') as f:
    data = yaml.safe_load(f)
    print(f'YAML is valid. Total services: {len(data["services"])}')
