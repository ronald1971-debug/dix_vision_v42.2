# Local AI Models Configuration Guide

## Overview

DIX VISION Desktop AgentOS supports local AI models for privacy-focused offline operation. This guide explains how to configure and use local models for LLM, STT, and TTS.

## Supported Local Models

### 1. LLM (Large Language Model)
- **llama.cpp** - GGUF format models
- **Models**: Llama 2, Llama 3, Mistral, CodeLlama, etc.

### 2. STT (Speech-to-Text)
- **whisper.cpp** - Whisper models
- **Faster-Whisper** - Faster Whisper implementation
- **Models**: base, small, medium, large

### 3. TTS (Text-to-Speech)
- **Piper** - High-quality offline TTS
- **Models**: Various voice models in English and other languages

## Installation Guide

### Step 1: Install llama.cpp

#### Option A: Pre-built Binaries
```bash
# Download from GitHub Releases
# Visit: https://github.com/ggerganov/llama.cpp/releases

# For Windows:
# Download llama-bin-*.zip
# Extract to C:\llama.cpp
```

#### Option B: Build from Source
```bash
# Clone repository
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp

# Build (requires CMake)
mkdir build
cd build
cmake ..
cmake --build . --config Release
```

### Step 2: Download LLM Models

#### Recommended Models for DIX VISION:

**For General Purpose:**
- Llama 3 8B Instruct: https://huggingface.co/QuantFactory/Meta-Llama-3-8B-Instruct-GGUF
- Mistral 7B Instruct: https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF

**For Code/Engineering:**
- CodeLlama 7B Instruct: https://huggingface.co/TheBloke/CodeLlama-7B-Instruct-GGUF
- DeepSeek Coder: https://huggingface.co/m-a-p/DeepSeek-Coder-V2-Lite-Instruct-GGUF

**For Trading/Finance:**
- Financial models from HuggingFace

#### Download Command:
```bash
# Using huggingface-cli
pip install huggingface-cli

# Download Llama 3 8B Instruct (Q4_K_M format - good balance of speed/quality)
huggingface-cli download QuantFactory/Meta-Llama-3-8B-Instruct-GGUF Meta-Llama-3-8B-Instruct.Q4_K_M.gguf --local-dir ./models
```

### Step 3: Install Whisper

#### Option A: Faster-Whisper (Recommended)
```bash
pip install faster-whisper
```

#### Option B: whisper.cpp
```bash
# Download pre-built binaries
# Visit: https://github.com/ggerganov/whisper.cpp/releases

# For Windows, download whisper-bin-*.zip
```

#### Download Whisper Models:
```bash
# Base model (fast, good accuracy)
# Faster-Whisper will download automatically on first use
```

### Step 4: Install Piper TTS

#### Installation:
```bash
# Using npm (already integrated with Komorebi)
cd komorebi_desktop
npm run fetch:piper

# Or manual installation
pip install piper-tts
```

#### Download Voice Models:
```bash
# English voices
# Download from: https://huggingface.co/rhasspy/piper-voices

# Example: Lessac medium male voice
# huggingface-cli download rhasspy/piper-voices en_US-lessac-medium --local-dir ./voices
```

## Configuration

### Update `desktop_agent_config.yaml`

```yaml
# Local LLM Configuration
local_llm:
  enabled: true
  backend: "llama.cpp"
  model_path: "./models/Meta-Llama-3-8B-Instruct.Q4_K_M.gguf"
  
  # Model parameters
  context_length: 4096
  temperature: 0.7
  top_p: 0.9
  max_tokens: 2048
  
  # Performance
  n_gpu_layers: 0  # Set to -1 for all GPU layers, 0 for CPU only
  n_batch: 512
  n_threads: 4

# Local STT Configuration
local_stt:
  enabled: true
  backend: "faster-whisper"
  model_size: "base"  # tiny, base, small, medium, large
  device: "cpu"  # cpu, cuda
  
  # Language
  language: "en"
  task: "transcribe"

# Local TTS Configuration
local_tts:
  enabled: true
  backend: "piper"
  model_path: "./voices/en_US-lessac-medium"
  speaker_id: 0
  
  # Audio settings
  sample_rate: 22050
  output_format: "wav"
  
  # Speech synthesis
  speed: 1.0
  noise_scale: 0.667
  noise_w: 0.8
```

## Model Performance Guide

### Hardware Recommendations

#### For CPU-only operation:
- **LLM**: 7B parameters minimum (8GB RAM required)
- **STT**: base model (2GB RAM)
- **TTS**: Any model (minimal RAM)

#### For GPU acceleration:
- **NVIDIA GPU**: 4GB+ VRAM for 7B models
- **AMD GPU**: ROCm support required
- **Apple Silicon**: Metal support (MPS)

### Model Size vs Performance

| Model Size | RAM Required | Speed | Quality | Use Case |
|------------|-------------|-------|---------|----------|
| 3B | 4GB | Fast | Good | Quick tasks |
| 7B | 8GB | Medium | Very Good | General purpose |
| 13B | 16GB | Slow | Excellent | Complex tasks |
| 34B | 32GB | Very Slow | Excellent | Professional use |

## Testing Local Models

### Test LLM:
```bash
# Using llama.cpp
./main -m models/Meta-Llama-3-8B-Instruct.Q4_K_M.gguf -p "Hello, how are you?"
```

### Test STT:
```python
from faster_whisper import WhisperModel

model = WhisperModel("base", device="cpu", compute_type="int8")
segments, info = model.transcribe("audio.wav")
print(segments)
```

### Test TTS:
```python
from piper import Piper

model = Piper.load("en_US-lessac-medium")
model.synthesize("Hello world", "output.wav")
```

## Troubleshooting

### Model Not Loading
1. Check file path is correct
2. Verify model file is complete (check file size)
3. Ensure sufficient RAM
4. Check llama.cpp version compatibility

### Slow Performance
1. Enable GPU acceleration if available
2. Use smaller model (quantization)
3. Reduce context length
4. Adjust batch size
5. Close other applications

### Out of Memory Errors
1. Use smaller model
2. Reduce n_batch parameter
3. Reduce context_length
4. Use quantized models (Q4_K_M, Q3_K_S)

### Poor Quality Output
1. Use larger model
2. Adjust temperature parameter
3. Increase context length
4. Use better quantization (Q5_K_M, Q6_K)

## Model Sources

### LLM Models (GGUF Format)
- HuggingFace: https://huggingface.co/models?search=gguf
- TheBloke: https://huggingface.co/TheBloke
- QuantFactory: https://huggingface.co/QuantFactory

### Whisper Models
- HuggingFace: https://huggingface.co/Systran
- OpenAI: https://github.com/openai/whisper

### Piper Voice Models
- HuggingFace: https://huggingface.co/rhasspy/piper-voices

## Security Notes

- Only download models from trusted sources
- Verify model checksums when available
- Keep models updated for security patches
- Don't share sensitive data with unknown models
- Review model licenses before commercial use

## Performance Tuning

### For DIX VISION Desktop AgentOS:

**INDIRA Agent (Market Research):**
- Model: Llama 3 8B or Mistral 7B
- Quantization: Q4_K_M (balance)
- Context: 4096 tokens
- Focus: Quality over speed

**DYON Agent (Engineering):**
- Model: CodeLlama 7B or DeepSeek Coder
- Quantization: Q4_K_M
- Context: 8192 tokens (for longer code)
- Focus: Code accuracy

**Voice Interaction:**
- STT: Whisper base (fast enough)
- TTS: Piper medium (good quality)
- Latency: < 500ms preferred

## Hybrid Setup (Local + Cloud)

For optimal performance:

1. **Use local for:**
   - Privacy-sensitive tasks
   - Offline operation
   - Quick interactions
   - Routine automation

2. **Use cloud for:**
   - Complex reasoning
   - Large context requirements
   - Multi-modal tasks (vision)
   - Cutting-edge capabilities

## Updates and Maintenance

### Updating Models:
```bash
# Check for newer model versions
huggingface-cli repo-info QuantFactory/Meta-Llama-3-8B-Instruct-GGUF

# Download updated model
huggingface-cli download ... --local-dir ./models --local-dir-use-symlinks
```

### Updating Backends:
```bash
# Update llama.cpp
cd llama.cpp
git pull
mkdir build && cd build
cmake .. && cmake --build . --config Release

# Update Python packages
pip install --upgrade faster-whisper piper-tts
```

## Resources

### Documentation
- llama.cpp: https://github.com/ggerganov/llama.cpp
- Whisper: https://github.com/openai/whisper
- Piper: https://github.com/rhasspy/piper

### Communities
- LocalLLaMA: https://reddit.com/r/LocalLLaMA
- Oobabooga: https://github.com/oobabooga/text-generation-webui

### Benchmarks
- LLM Benchmarks: https://huggingface.co/spaces/optimum/llm-perf-leaderboard
- Model Comparison: https://huggingface.co/models

## Support

For local model issues:
1. Check model compatibility
2. Verify installation
3. Review error logs
4. Consult documentation
5. Check system resources
