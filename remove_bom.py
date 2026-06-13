# Remove BOM from compose.yaml
with open('compose.yaml', 'r', encoding='utf-8-sig') as f:
    content = f.read()

with open('compose.yaml', 'w', encoding='utf-8') as f:
    f.write(content)

print('BOM removed and file saved with UTF-8 encoding')
