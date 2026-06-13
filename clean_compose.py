import yaml

# Read the compose.yaml file
with open('compose.yaml', 'r', encoding='utf-8-sig') as f:
    content = f.read()

# Remove BOM if present
lines = content.split('\n')
if lines[0].startswith('\ufeff'):
    lines[0] = lines[0][1:]
    print('Removed BOM from first line')

# Ensure version is properly formatted
if lines[0].strip() == 'version: 3.8' or lines[0].strip().startswith('version'):
    lines[0] = 'version: 3.8'

# Write back without BOM
clean_content = '\n'.join(lines)
with open('compose_clean.yaml', 'w', encoding='utf-8') as f:
    f.write(clean_content)

print('Created compose_clean.yaml')

# Validate the clean file
with open('compose_clean.yaml', 'r') as f:
    data = yaml.safe_load(f)
    print(f'Validation successful. Total services: {len(data["services"])}')
