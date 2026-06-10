# Live2D Avatar Customization Guide

## Overview

The DIX VISION Desktop AgentOS uses Live2D Cubism models for the interactive avatar. This guide explains how to customize the avatar to match your preferences or branding.

## Current Avatar Location

The default avatar is located at:
```
komorebi_desktop/public/live2d/mao_pro/
```

## Avatar Structure

A Live2D model consists of:

```
live2d/model_name/
├── model_name.moc3                 # Compiled model file
├── model_name.model3.json          # Model settings
├── model_name.physics3.json       # Physics settings
├── model_name.pose3.json           # Pose settings
├── textures/
│   └── texture_00.png             # Texture images
├── motions/
│   ├── mtn_01.motion3.json        # Idle motions
│   ├── mtn_02.motion3.json        # Tap motions
│   └── special_01.motion3.json    # Special motions
└── expressions/
    ├── exp_01.exp3.json          # Normal expression
    ├── exp_02.exp3.json          # Happy expression
    └── exp_03.exp3.json          # Angry expression
```

## Customization Options

### Option 1: Use Existing Live2D Models

You can download free Live2D models from:

1. **Live2D Cubism**
   - Visit: https://www.live2d.com/en/download/cubism_sdk/
   - Download sample models from the Cubism SDK

2. **Live2D Official Models**
   - Visit: https://www.live2d.com/en/
   - Check for free model releases

3. **Community Models**
   - Booth (Japanese): https://booth.pm/
   - Search for "Live2D model" or "Live2D モデル"

### Option 2: Create Your Own Live2D Model

To create a custom Live2D model:

1. **Download Live2D Cubism Editor**
   - Free version: https://www.live2d.com/en/download/cubism/
   - Pro version (for commercial use): https://www.live2d.com/en/download/cubism/pro/

2. **Create Your Artwork**
   - Draw your character in layers (separate eye, mouth, hair, etc.)
   - Save as PSD (Photoshop) or separate PNG files
   - Follow Live2D layering guidelines

3. **Import to Cubism Editor**
   - Import your artwork
   - Set up deformers for animation
   - Create motions and expressions
   - Export as .moc3 and .json files

### Option 3: Hire a Live2D Artist

If you want a professional custom model:

1. **Find Artists**
   - Fiverr: https://www.fiverr.com/search/services?query=live2d
   - Upwork: https://www.upwork.com/
   - Twitter/X: Search #Live2DCommission
   - DeviantArt: Live2D community

2. **Provide Specifications**
   - Character design references
   - Expression requirements (happy, sad, angry, etc.)
   - Motion requirements (idle, tap, talk)
   - Budget and timeline

## How to Replace the Avatar

### Step 1: Prepare Your Model

1. Ensure your model is in Live2D Cubism 2.1, 3.0, 4.0, or 5.0 format
2. Verify all required files are present:
   - `.moc3` file
   - `.model3.json` file
   - `.physics3.json` file (optional but recommended)
   - `.pose3.json` file (optional but recommended)
   - Texture files (PNG format)
   - Motion files (`.motion3.json`)
   - Expression files (`.exp3.json`)

### Step 2: Replace the Files

1. Create a new directory for your model:
```bash
cd komorebi_desktop/public/live2d
mkdir your_model_name
```

2. Copy your model files to the new directory:
```bash
# Copy all model files
cp /path/to/your/model/* komorebi_desktop/public/live2d/your_model_name/
```

### Step 3: Update Configuration

Edit the Live2D configuration in the frontend:

1. Open `komorebi_desktop/src/components/Live2DCanvas.tsx`
2. Find the model loading section
3. Update the model path:

```typescript
// Change from:
const modelPath = "/live2d/mao_pro/mao_pro.model3.json";

// To:
const modelPath = "/live2d/your_model_name/your_model.model3.json";
```

4. Save the file

### Step 4: Test the Avatar

Run the desktop app and verify the new avatar loads correctly:

```bash
cd komorebi_desktop
npm run tauri dev
```

## DIX VISION Branding

For DIX VISION specific branding, consider:

### Color Scheme
- Primary: Deep purple (#6B21A8)
- Secondary: Blue (#3B82F6)
- Accent: Cyan (#06B6D4)
- Background: Dark (#0F172A)

### Character Concept
A futuristic AI assistant with:
- Glowing cybernetic elements
- Holographic interface elements
- Data stream visualizations
- Clean, modern aesthetic

### Expression Set
Required expressions for DIX VISION:
- Normal: Default state
- Thinking: Processing information
- Happy: Success/completion
- Confused: Need clarification
- Working: Agent activity
- Alert: Important notification
- Error: System issue

## Troubleshooting

### Avatar Not Loading

1. Check file paths in configuration
2. Verify all required files are present
3. Check browser console for errors
4. Ensure file permissions are correct

### Avatar Not Animating

1. Verify motion files are present
2. Check motion file format (should be .motion3.json)
3. Ensure expressions are properly configured
4. Test with default model to isolate issue

### Performance Issues

1. Reduce texture resolution
2. Optimize motion complexity
3. Reduce number of expressions
4. Use lighter model format

## Resources

### Official Documentation
- Live2D Cubism Documentation: https://docs.live2d.com/
- PixiJS Live2D Display: https://github.com/guansss/pixi-live2d-display

### Tutorials
- Live2D Official Tutorials: https://www.live2d.com/en/learn/
- YouTube Live2D Tutorials: Search "Live2D tutorial"

### Communities
- Live2D Discord: https://discord.gg/live2d
- Reddit: r/Live2D

## Support

If you encounter issues with avatar customization:
1. Check the official Live2D documentation
2. Review the error messages in the browser console
3. Test with the default model first
4. Consult the Komorebi GitHub issues

## Notes

- The avatar system supports Cubism 2, 3, 4, and 5 formats
- Lipsync is automatically handled by the system
- Eye tracking follows the mouse cursor
- Tap gestures trigger animations
- Expressions change based on AI responses
