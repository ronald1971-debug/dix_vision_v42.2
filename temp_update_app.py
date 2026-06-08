with open('C:/Users/prive/OneDrive/Documents/GitHub/dixvision-1/dashboard2026/src/App.tsx', encoding='utf-8') as f:
    lines = f.readlines()

# Add import after HazardsPage
for i, line in enumerate(lines):
    if 'import { HazardsPage }' in line:
        lines.insert(i + 1, 'import { OpenOrdersFillsPage } from \"@/pages/OpenOrdersFillsPage\";\n')
        break

# Add route case after hazards
for i, line in enumerate(lines):
    if 'case \"hazards\":' in line:
        # Find the next line which should be the return statement
        if i + 1 < len(lines) and 'return <HazardsPage />' in lines[i + 1]:
            lines.insert(i + 2, '    case \"orders-fills\":\n')
            lines.insert(i + 3, '      return <OpenOrdersFillsPage />;\n')
        break

# Add hotkey after go-hazards
for i, line in enumerate(lines):
    if '\"go-hazards\": () => goRoute(\"hazards\"),' in line:
        lines.insert(i + 1, '    \"go-orders-fills\": () => goRoute(\"orders-fills\"),\n')
        break

with open('C:/Users/prive/OneDrive/Documents/GitHub/dixvision-1/dashboard2026/src/App.tsx', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('Updated App.tsx')
