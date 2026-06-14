import yaml

# Read the current compose.yaml
with open('compose.yaml', 'r') as f:
    data = yaml.safe_load(f)

# Add the Desktop Agent service as service #101
desktop_agent_service = {
    'build': {'context': './desktop_agent', 'dockerfile': 'Dockerfile'},
    'image': 'dix-desktop-agent:latest',
    'container_name': 'dix-desktop-agent-service',
    'ports': ['9186:9186'],
    'volumes': [
        './desktop_agent/app_data:/app/data',
        './desktop_agent/logs:/app/logs',
        './desktop_agent/config:/app/config',
        './desktop_agent/learning:/app/learning'
    ],
    'environment': [
        'DESKTOP_AGENT_LOG_LEVEL=INFO',
        'DASHBOARD_URL=http://dashboard2026-service:9003',
    ],
    'restart': 'unless-stopped',
    'networks': ['dixvision-network'],
    'healthcheck': {
        'test': ['CMD', 'python', '-c', 'import requests; requests.get("http://localhost:9186/health")'],
        'interval': '30s',
        'timeout': '10s',
        'retries': 3
    },
    'deploy': {
        'resources': {
            'limits': {'cpus': '2.0', 'memory': '2G'},
            'reservations': {'cpus': '1.0', 'memory': '1G'}
        }
    }
}

# Add to services
data['services']['desktop-agent-service'] = desktop_agent_service

# Write back to compose.yaml
with open('compose.yaml', 'w') as f:
    yaml.dump(data, f, default_flow_style=False)

print("Desktop Agent service added to compose.yaml as service #101")
print(f"Total services: {len(data['services'])}")
