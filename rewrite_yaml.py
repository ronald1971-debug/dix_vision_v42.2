import yaml

# Read the compose.yaml with UTF-8-SIG encoding to handle BOM
with open('compose.yaml', 'r', encoding='utf-8-sig') as f:
    data = yaml.safe_load(f)

# Write back with clean UTF-8 encoding
with open('compose.yaml', 'w', encoding='utf-8') as f:
    yaml.dump(data, f, default_flow_style=False, sort_keys=False)

print('Rewrote compose.yaml with clean UTF-8 encoding')
print(f'Total services: {len(data["services"])}')
