import yaml

# Read the current compose.yaml (with BOM)
with open('compose.yaml', 'r', encoding='utf-8-sig') as f:
    data = yaml.safe_load(f)

# Ensure proper version field
if 'version' in data:
    # Remove any BOM-prefixed version if it exists
    version_keys = [k for k in data.keys() if k.startswith('\ufeff') or 'version' in k.lower()]
    for key in version_keys:
        del data[key]
    
    # Add clean version
    data['version'] = '3.8'

# Write clean YAML
with open('compose_fixed.yaml', 'w', encoding='utf-8') as f:
    yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

print('Created compose_fixed.yaml')

# Validate
with open('compose_fixed.yaml', 'r') as f:
    data_check = yaml.safe_load(f)
    print(f'Validation successful. Total services: {len(data_check["services"])}')
    print(f'Version: {data_check["version"]}')
