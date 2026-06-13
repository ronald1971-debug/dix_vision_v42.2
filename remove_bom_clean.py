with open('compose.yaml', 'r', encoding='utf-8-sig') as f:
    content = f.read()

with open('compose_new.yaml', 'w', encoding='utf-8') as f:
    f.write(content)

print('Created compose_new.yaml without BOM')
