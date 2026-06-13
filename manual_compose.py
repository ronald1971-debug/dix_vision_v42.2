import yaml

# Read the current compose.yaml (with BOM)
with open('compose.yaml', 'r', encoding='utf-8-sig') as f:
    data = yaml.safe_load(f)

# Create a completely clean YAML file
with open('compose_manual.yaml', 'w', encoding='utf-8') as f:
    f.write('version: 3.8\n\n')
    yaml.dump(data['services'], f, default_flow_style=False, sort_keys=False)
    f.write('\n')
    yaml.dump({'networks': data['networks']}, f, default_flow_style=False, sort_keys=False)
    f.write('\n')
    yaml.dump({'volumes': data['volumes']}, f, default_flow_style=False, sort_keys=False)

print('Created compose_manual.yaml with manual construction')

# Validate
with open('compose_manual.yaml', 'r') as f:
    data_check = yaml.safe_load(f)
    print(f'Validation successful. Total services: {len(data_check["services"])}')
