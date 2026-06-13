# Read the file in binary mode
with open('compose.yaml', 'rb') as f:
    content = f.read()

# Remove BOM if present
if content[:3] == b'\xef\xbb\xbf':
    content = content[3:]
    print('Removed BOM from file')
else:
    print('No BOM found')

# Write back without BOM
with open('compose_bom_free.yaml', 'wb') as f:
    f.write(content)

print('Created compose_bom_free.yaml')

# Validate with YAML
import yaml
with open('compose_bom_free.yaml', 'r') as f:
    data = yaml.safe_load(f)
    print(f'YAML validation successful. Total services: {len(data["services"])}')
