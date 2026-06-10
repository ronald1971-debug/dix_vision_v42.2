# DIX VISION Desktop AgentOS - Complete User Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Architecture Overview](#architecture-overview)
4. [Agent System](#agent-system)
5. [Browser Automation](#browser-automation)
6. [Voice Interaction](#voice-interaction)
7. [Skill System](#skill-system)
8. [Governance & Security](#governance--security)
9. [Configuration](#configuration)
10. [Troubleshooting](#troubleshooting)
11. [API Reference](#api-reference)

---

## Introduction

DIX VISION Desktop AgentOS is a comprehensive cognitive environment platform that enables INDIRA (Browser Intelligence Agent) and DYON (Engineering Intelligence Agent) to interact with browsers, desktop applications, and other cognitive environments through governed and observable interfaces.

### Key Features

- **Interactive Desktop**: Live2D avatar with voice interaction
- **Dual Agent System**: INDIRA for market research, DYON for engineering
- **Browser Automation**: Advanced web interaction and data extraction
- **Desktop Control**: Application automation and system integration
- **Hybrid AI**: Local models for privacy + cloud for power
- **Skill System**: Extensible automation capabilities
- **Governance Layer**: Policy enforcement and risk management
- **Complete Observability**: Transparent monitoring and logging

### What DIX VISION Is

- ✅ A cognitive operating environment
- ✅ A browser cognition system  
- ✅ An agent orchestration platform
- ✅ A governed automation runtime

### What DIX VISION Is Not

- ❌ A simple desktop assistant
- ❌ A basic chatbot
- ❌ A browser bot

---

## Getting Started

### System Requirements

#### Minimum Requirements
- **OS**: Windows 10/11, macOS 10.15+, Linux
- **RAM**: 8GB (16GB recommended for local models)
- **Storage**: 10GB free space
- **CPU**: 4 cores (8 cores recommended)
- **GPU**: Optional (for GPU acceleration)

#### Software Requirements
- Python 3.8+
- Node.js 18+
- Optional: CUDA (for NVIDIA GPU acceleration)

### Installation

#### Step 1: Clone/Download Repository
```bash
cd C:\dix_vision_v42.2
```

#### Step 2: Install Python Dependencies
```bash
pip install -r requirements.txt
```

#### Step 3: Install Frontend Dependencies
```bash
cd komorebi_desktop
npm install
```

#### Step 4: Configure API Keys (Optional)
```bash
cp .env.example .env
# Edit .env with your API keys
```

#### Step 5: Launch Application
**Method 1: Desktop Shortcut**
- Double-click "DIX VISION Desktop.lnk"

**Method 2: Python Launcher**
```bash
cd C:\dix_vision_v42.2
python launch_dix_vision_desktop.py
```

**Method 3: Tauri Development**
```bash
cd komorebi_desktop
npm run tauri dev
```

### First Launch

On first launch, you will see:
1. Live2D avatar initialization
2. Backend agent startup
3. System tray icon
4. Welcome message from the system

---

## Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────┐
│                  Desktop Frontend                    │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │ Live2D Avatar│  │ Chat Interface│  │ Settings    │ │
│  └──────────────┘  └──────────────┘  └────────────┘ │
└───────────────────────────┬─────────────────────────┘
                            │
                    ┌───────▼────────┐
                    │  Tauri Bridge  │
                    └───────┬────────┘
                            │
┌───────────────────────────▼─────────────────────────┐
│              Desktop AgentOS Backend                 │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │ Agent Runtime│  │ INDIRA Agent │  │ DYON Agent │ │
│  └──────────────┘  └──────────────┘  └────────────┘ │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │ Environment  │  │ Skill System │  │ Memory     │ │
│  │   Layer      │  │              │  │  System    │ │
│  └──────────────┘  └──────────────┘  └────────────┘ │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │  Governance  │  │  Telemetry   │  │  Vision    │ │
│  │   Layer      │  │   System     │  │   System   │ │
│  └──────────────┘  └──────────────┘  └────────────┘ │
└───────────────────────────┬─────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────┐
│              External Services                       │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │ Local Models │  │  Cloud APIs  │  │  Browser    │ │
│  │ (llama.cpp)  │  │ (OpenRouter) │  │ Automation │ │
│  └──────────────┘  └──────────────┘  └────────────┘ │
└─────────────────────────────────────────────────────┘
```

### Data Flow

1. **User Input** → Voice/Text/Click
2. **Frontend** → Tauri IPC → Backend
3. **Backend** → Agent Processing
4. **Agents** → Skills/Environments
5. **Response** → Frontend → Avatar/Output

---

## Agent System

### INDIRA Agent (Browser Intelligence)

INDIRA specializes in market research, trading analysis, and knowledge discovery through browser-based cognitive environments.

#### Capabilities

- **Market Research**: Cryptocurrency and market data analysis
- **Trader Analysis**: Wallet behavior and pattern recognition  
- **Strategy Research**: Trading strategy development and testing
- **Narrative Research**: Market sentiment and news analysis
- **Knowledge Discovery**: Information synthesis and insight generation

#### Usage Example

```python
from desktop_agent.agents import INDIRAAgent

# Initialize agent
indira = INDIRAAgent(runtime)
await indira.initialize()

# Research a cryptocurrency
results = await indira.research_market("BTC")
print(results)
```

### DYON Agent (Engineering Intelligence)

DYON specializes in code analysis, repository understanding, and automation generation.

#### Capabilities

- **Repository Analysis**: Code structure and quality assessment
- **Architecture Analysis**: Design pattern identification
- **Skill Creation**: Automated skill generation
- **Automation Creation**: Workflow and connector development
- **Code Evolution**: Suggested improvements and refactoring

#### Usage Example

```python
from desktop_agent.agents import DYONAgent

# Initialize agent
dyon = DYONAgent(runtime)
await dyon.initialize()

# Analyze a repository
analysis = await dyon.analyze_repository("./my_project")
print(analysis)
```

---

## Browser Automation

### Setup

Configure browser automation in `desktop_agent_config.yaml`:

```yaml
browser:
  headless: true
  browser_type: "chrome"
  automation:
    enabled: true
```

### Basic Operations

```python
from desktop_agent.browser import BrowserCognitiveBridge

# Create browser bridge
browser = BrowserCognitiveBridge()
await browser.connect()

# Navigate to URL
await browser.navigate("https://example.com")

# Extract data
text = await browser.extract_text()
elements = await browser.search("button")

# Interact
await browser.click_element("#submit-button")
await browser.type_text("#search-input", "search terms")
```

### Advanced Features

- **Multi-tab management**
- **Cookie handling**
- **Screenshot capture**
- **JavaScript execution**
- **Form filling**
- **Data extraction**

---

## Voice Interaction

### Voice System Configuration

```yaml
voice:
  enabled: true
  wake_word: "indira"
  
  stt:
    engine: "whisper"
    language: "en"
    
  tts:
    engine: "piper"
    voice: "en_US-lessac-medium"
```

### Voice Commands

**Operator Commands:**
- "Indira, stop"
- "Indira, pause"
- "Indira, show settings"

**Agent Commands:**
- "Indira, research Bitcoin"
- "DYON, analyze this repository"

**Mission Commands:**
- "Start market monitoring"
- "Enable trading mode"

---

## Skill System

### Using Built-in Skills

```python
from desktop_agent.skills import SkillRegistry

# Get skill registry
skills = runtime.skills

# Execute a skill
result = await skills.execute("research_coin", coin_symbol="BTC")
```

### Creating Custom Skills

1. Inherit from `Skill` base class
2. Implement `execute()` method
3. Define metadata
4. Register with `SkillRegistry`

Example:
```python
from desktop_agent.skills import Skill, SkillMetadata

class MyCustomSkill(Skill):
    async def execute(self, **kwargs):
        # Your skill logic
        return {"result": "success"}
        
    def get_metadata(self):
        return SkillMetadata(
            id="my_skill",
            name="My Custom Skill",
            description="Description",
            category="custom",
            version="1.0.0",
            author="You",
            parameters={"required": [], "optional": []},
            dependencies=[],
        )
```

### Available Custom Skills

- **Research Coin**: Cryptocurrency research
- **Analyze Wallet**: Wallet behavior analysis  
- **Analyze Repository**: Code repository analysis

---

## Governance & Security

### Policy Enforcement

All agent actions are subject to governance policies:

```yaml
governance:
  enabled: true
  policies:
    safety:
      enabled: true
      require_human_approval: true
```

### Risk Assessment

High-risk actions require approval:
- System modifications
- Large file operations
- Network access
- Financial transactions

### Audit Trail

All actions are logged with:
- Timestamp
- Agent identity
- Action details
- Approval status
- Result

---

## Configuration

### Main Configuration File

`desktop_agent_config.yaml` - Backend configuration

### Frontend Configuration

`komorebi_desktop/src-tauri/tauri.conf.json` - Tauri app configuration

### Environment Variables

`komorebi_desktop/.env` - API keys and secrets

### Configuration Priority

1. Environment variables
2. .env file
3. Configuration files
4. Default values

---

## Troubleshooting

### Common Issues

**Application won't start:**
1. Check logs in `dix_vision_desktop.log`
2. Verify Node.js and Python are installed
3. Ensure dependencies are installed

**Avatar not loading:**
1. Check Live2D model files are present
2. Verify model path in configuration
3. Check browser console for errors

**Voice not working:**
1. Check microphone permissions
2. Verify audio devices
3. Test with different STT engine

**Browser automation fails:**
1. Ensure browser automation libraries are installed
2. Check browser driver compatibility
3. Verify headless mode works

**Agents not responding:**
1. Check agent initialization in logs
2. Verify runtime is running
3. Check event bus connectivity

### Log Locations

- **Backend**: `dix_vision_desktop.log`
- **Frontend**: Browser console (F12)
- **System**: Windows Event Viewer

### Getting Help

1. Check documentation files
2. Review error logs
3. Test with minimal configuration
4. Check GitHub issues

---

## API Reference

### Python Backend API

#### AgentRuntime
```python
class AgentRuntime:
    async def initialize() -> None
    async def start() -> None
    async def stop() -> None
    def register_agent(name: str, agent: Any) -> None
    def get_agent(name: str) -> Optional[Any]
```

#### EnvironmentInterface
```python
class EnvironmentInterface:
    async def connect() -> bool
    async def disconnect() -> None
    async def observe() -> StateSnapshot
    async def search(query: str) -> List[Element]
    async def navigate(target: str) -> bool
    async def interact(element: Element, action: str) -> bool
```

#### Skill
```python
class Skill:
    async def execute(**kwargs) -> Any
    def get_metadata() -> SkillMetadata
    async def validate_parameters(parameters: Dict) -> bool
```

### Frontend API (Tauri Commands)

Refer to `komorebi_desktop/src-tauri/src/commands/` for available Tauri commands.

---

## Support & Community

### Documentation Files

- `DIX_VISION_DESKTOP_INTEGRATION_COMPLETE.md` - Integration guide
- `LIVE2D_CUSTOMIZATION_GUIDE.md` - Avatar customization
- `local_models_setup.md` - Local AI models setup
- `desktopupdate.txt` - Original build plan

### Resources

- Komorebi Documentation: `komorebi_desktop/README.md`
- Python Package Index: PyPI
- Node Package Manager: npmjs.com

### Best Practices

1. **Security**: Never commit API keys
2. **Privacy**: Use local models for sensitive data
3. **Performance**: Monitor resource usage
4. **Testing**: Test skills in sandbox first
5. **Backup**: Backup configuration and data regularly

---

## Conclusion

DIX VISION Desktop AgentOS provides a powerful, governed environment for cognitive agents to interact with digital systems. With proper configuration and usage, it can significantly enhance productivity while maintaining security and privacy.

For questions or issues, refer to the troubleshooting section or check the log files for detailed error information.
