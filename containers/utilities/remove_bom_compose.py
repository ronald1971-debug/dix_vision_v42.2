import codecs

# Read the file with BOM encoding
with open('C:/dix_vision_v42.2/compose.yaml', 'r', encoding='utf-8-sig') as f:
    content = f.read()

# Write back without BOM
with open('C:/dix_vision_v42.2/compose.yaml', 'w', encoding='utf-8') as f:
    f.write(content)

print("BOM removed from compose.yaml")
