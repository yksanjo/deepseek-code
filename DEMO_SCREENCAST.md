# Demo & Screencast Guide | 演示与屏幕录制指南

This guide shows you how to create demos and screencasts for DeepSeek Code.

本指南向您展示如何为 DeepSeek Code 创建演示和屏幕录制。

---

## Quick Demo Commands | 快速演示命令

### 1. Interactive Mode Demo

```bash
# Start interactive mode
deepseek-code

# Try these commands:
> Create a simple calculator in Python
> Add docstrings to all functions
> Find all files with "test" in the name
```

### 2. Single Task Demo

```bash
# Run a single task
deepseek-code run "Add type hints to main.py"
```

### 3. Trust Mode Demo

```bash
# Auto-approve safe operations
deepseek-code run --trust "Refactor the authentication module"
```

### 4. YOLO Mode Demo

```bash
# Skip all prompts (like Claude Code)
deepseek-code run --yolo "Generate a complete REST API"
```

---

## Creating GIF Demos | 创建 GIF 演示

### Option 1: Using LiceCap (macOS)

1. Download [LiceCap](https://www.apptorium.com/licecap)
2. Select the recording area
3. Click Record and perform your demo
4. Save as GIF

### Option 2: Using Giphy Capture

1. Download [Giphy Capture](https://giphy.com/apps/giphycapture)
2. Select area to record
3. Record your demo
4. Upload to Giphy or save locally

### Option 3: Using FFmpeg (CLI)

```bash
# Record screen to video
ffmpeg -f avfoundation -i "1" -t 30 output.mov

# Convert to GIF
ffmpeg -i output.mov -vf "fps=10,scale=800:-1:flags=lanczos" output.gif

# Optimize GIF
gifsicle -O3 output.gif -o optimized.gif
```

### Option 4: Using asciinema (Terminal Recording)

```bash
# Install asciinema
brew install asciinema

# Record terminal session
asciinema rec demo.json

# Convert to animated GIF
asciinema cat demo.json | gifify > demo.gif
```

---

## Recommended Demo Scripts | 推荐演示脚本

### Demo 1: Basic Usage

```
# Start
deepseek-code

# Task 1: Read a file
> Read the main.py file

# Task 2: Create a simple function
> Create a function that calculates fibonacci numbers

# Task 3: Edit existing code
> Add type hints to the function
```

### Demo 2: Permission System

```
# Show default mode (asks for permission)
deepseek-code
> write_file: test.py

# Show Trust mode
deepseek-code run --trust "Create a new file"

# Show YOLO mode
deepseek-code run --yolo "Generate a complete module"
```

### Demo 3: Code Search

```
deepseek-code

# Find Python files
> Find all Python files in this project

# Search for patterns
> Find all functions that start with "test"

# Read multiple files
> Show me the contents of config.py and settings.py
```

---

## Screencast Tips | 屏幕录制技巧

### Terminal Settings
- Use a dark theme (Solarized Dark or Monokai)
- Increase font size to 16px+
- Use a monospace font (Fira Code, JetBrains Mono)

### Recording Setup
- Resolution: 1920x1080 or 1280x720
- Frame rate: 30fps for video, 10-15fps for GIF
- Show cursor during recording

### Editing
- Trim silence at beginning/end
- Add highlights with arrows or circles
- Include subtitles for key actions

---

## Sharing Your Demo | 分享您的演示

### Video Platforms
- YouTube
- Loom
- Vimeo

### GIF Hosting
- Giphy
- Imgur
- GitHub Issues/READMEs

### Embed in README

```markdown
![Demo](docs/demo.gif)
```

---

## Want to Contribute a Demo? | 想贡献演示吗?

We welcome community demos! Share your recordings:

1. Open an issue at https://github.com/yksanjo/deepseek-code/issues
2. Upload your demo to a sharing service
3. We'll add it to the official showcase

---

## Placeholder for Future Demos | 未来演示占位符

### Interactive Mode Demo
![Interactive Mode](https://via.placeholder.com/800x450?text=Interactive+Mode+Demo+GIF)

### Permission System Demo
![Permissions](https://via.placeholder.com/800x450?text=Permission+System+Demo+GIF)

### YOLO Mode Demo
![YOLO Mode](https://via.placeholder.com/800x450?text=YOLO+Mode+Demo+GIF)
