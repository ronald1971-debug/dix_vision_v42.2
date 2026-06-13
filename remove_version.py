import yaml

# Read the current compose.yaml 
with open('compose.yaml', 'r') as f:
    data = yaml.safe_load(f)

# Remove version field (docker-compose v5 doesn't require it)
if 'version' in data:
    del data['version']
    # Also remove any BOM-prefixed version keys
    version_keys = [k for k in list(data.keys()) if 'version' in k.lower()]
    for key in version_keys:
        del data[key]

# Write without version
with open('compose_no_version.yaml', 'w', encoding='utf-8') as f:
    yaml.dump(data, f, default_flow_style=False, sort_keys=False)

print('Created compose_no_version.yaml')

# Validate
with open('compose_no_version.yaml', 'r') as f:
    data_check = yaml.safe_load(f)
    print(f'YAML validation successful. Total services: {len(data_check["services"])}')
