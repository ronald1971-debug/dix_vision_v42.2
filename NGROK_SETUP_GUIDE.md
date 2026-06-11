# NGROK SETUP INSTRUCTIONS

## Authentication Required

ngrok requires a verified account and authtoken. Here's how to set it up:

## Step 1: Sign up for ngrok account
1. Go to: https://dashboard.ngrok.com/signup
2. Create a free account (you can use your email or GitHub account)

## Step 2: Get your authtoken
1. After signing in, go to: https://dashboard.ngrok.com/get-started/your-authtoken
2. Copy your authtoken (it will look like: `2aB3cD4eF5gH6iJ7kL8mN9oP0qR1sT2uV3wX4yZ5aB`)

## Step 3: Configure ngrok

### Option A: Set authtoken globally
```powershell
ngrok config add-authtoken YOUR_AUTH_TOKEN_HERE
```

### Option B: Set authtoken for this session only
```powershell
ngrok http 8080 --authtoken YOUR_AUTH_TOKEN_HERE
```

## Step 4: Start ngrok tunnel
```powershell
ngrok http 8080
```

This will give you a public URL like: `https://random-name.ngrok.io` that forwards to your local port 8080.

## Step 5: Use your API with authentication

Your API now has authentication enabled. To access it via ngrok:

### API Key
- **Default Key**: `dixvision-secret-key-2024`
- **Environment Variable**: You can set `DIXVISION_API_KEY` to use your own key

### Headers
Include this header in your requests:
```
X-API-Key: dixvision-secret-key-2024
```

### Example Request
```bash
curl -H "X-API-Key: dixvision-secret-key-2024" https://your-ngrok-url.ngrok.io/api/compliance/config
```

### Example with curl
```bash
# Get compliance config
curl -H "X-API-Key: dixvision-secret-key-2024" https://your-ngrok-url.ngrok.io/api/compliance/config

# Set compliance level
curl -X POST -H "X-API-Key: dixvision-secret-key-2024" \
  -H "Content-Type: application/json" \
  -d '{"level": 75}' \
  https://your-ngrok-url.ngrok.io/api/compliance/set
```

### Example with JavaScript
```javascript
const headers = {
  'X-API-Key': 'dixvision-secret-key-2024',
  'Content-Type': 'application/json'
};

fetch('https://your-ngrok-url.ngrok.io/api/compliance/config', { headers })
  .then(response => response.json())
  .then(data => console.log(data));
```

## Security Notes

### Protected Endpoints
The following endpoints now require API key authentication:
- `/api/compliance/set` - Set compliance level
- `/api/tick` - Market tick input
- `/api/signal` - Signal event input
- `/api/admin/learning/tick` - Admin learning tick
- `/api/credentials/verify` - Credential verification

### Public Endpoints (No auth required)
- `/` - Dashboard redirect
- `/api/health` - Health check
- `/api/compliance/config` - Get compliance config (read-only)
- `/api/compliance/weights` - Get compliance weights (read-only)
- `/api/kernel/state` - Kernel state (read-only)
- `/api/runtime/status` - Runtime status (read-only)
- `/api/registry/engines` - Registry engines (read-only)
- `/api/registry/plugins` - Registry plugins (read-only)
- `/api/ai/providers` - AI providers (read-only)

### Local Development (Disable Auth)
If you want to disable authentication for local development:
```powershell
# Set environment variable
$env:DISABLE_AUTH = "true"

# Then start your server
python -m uvicorn ui.server:app --reload --port 8080
```

## Alternative: Local Network Access

If you only need access on your local network (not internet), use simple tunneling:

```powershell
# Run the simple tunnel script
python c:/dix_vision_v42.2/simple_tunnel.py 8888
```

Then access via: `http://YOUR_LAN_IP:8888`

Your local IP is: `192.168.81.52`

## Current Protected Services

✅ **Authentication Added**:
- Compliance management (set requires auth, get is public)
- Trading operations (tick, signal require auth)
- Admin functions (learning tick requires auth)
- Credential management (verify requires auth)

🔒 **Security Level**: Medium - API key authentication for critical operations

🌐 **Exposure**: Ready for ngrok once you set up your authtoken