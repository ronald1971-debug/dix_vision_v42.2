with open('ui/cockpit_routes.py') as f:
    lines = f.readlines()

# Remove duplicate Phase 11.1 model sections
# Keep only the one after CustomStrategyActionIn (around line 185)
# Remove the ones at lines 90 and 138

output = []
skip_until = None
phase11_count = 0

for i, line in enumerate(lines):
    if '# Phase 11.1 Pydantic models' in line:
        phase11_count += 1
        if phase11_count == 3:
            # Keep this one (after CustomStrategyActionIn)
            output.append(line)
            continue
        else:
            # Skip this duplicate section
            skip_until = i
            # Skip until we find a class that's not a Phase 11.1 model
            for j in range(i+1, len(lines)):
                if 'class' in lines[j] and 'OrderSubmitIn' not in lines[j] and 'OrderCancelIn' not in lines[j] and 'OrderCancelAllIn' not in lines[j] and 'StrategyActionIn' not in lines[j] and 'PositionCloseIn' not in lines[j] and 'LedgerReplayIn' not in lines[j]:
                    skip_until = j
                    break
            continue

    if skip_until is not None and i <= skip_until:
        continue

    output.append(line)

with open('ui/cockpit_routes.py', 'w') as f:
    f.writelines(output)

print(f'Cleaned up duplicate Phase 11.1 models. Kept 1 of {phase11_count} sections.')
