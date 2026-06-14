#!/bin/bash
set -e

echo "Starting DIX VISION v42.2+ Desktop Agent..."
echo "Version: 42.2.0"
echo "Phase 1 Foundation Layer"

# Create necessary directories
mkdir -p /app/data /app/logs /app/config /app/learning

# Start the Desktop Agent engine
echo "Starting Desktop Agent engine..."
python3 -c "
import sys
sys.path.append('/app')
sys.path.append('/app/governance')
sys.path.append('/app/coordination_layer')
sys.path.append('/app/system')

import asyncio
from engine import DesktopAgentEngine

async def main():
    engine = DesktopAgentEngine()
    success = await engine.start()
    if success:
        print('Desktop Agent Engine started successfully')
        print('Phase 1 Foundation Layer operational')
        # Keep engine running
        while engine.is_running:
            await asyncio.sleep(1)
    else:
        print('Failed to start Desktop Agent Engine')
        sys.exit(1)

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print('Shutting down Desktop Agent Engine...')
    asyncio.run(engine.stop())
except Exception as e:
    print(f'Desktop Agent error: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
" || exit 1
