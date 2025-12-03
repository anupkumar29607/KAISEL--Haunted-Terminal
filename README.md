# KAISEL — The Haunted Terminal
*A violet-lit, reactive AI interface built for Kiroween 2025 (Costume Contest).*

KAISEL is a cinematic, spooky, violet-themed AI terminal with a heavy focus on visual polish.  
It blends a futuristic hacker terminal with “haunted” UI effects: reactive particle fields, neon glows, animated headers, and a soft blue-violet sweep that passes over the screen.

This project was built for the **Kiroween Costume Contest**, where the “costume” is the interface itself — a dramatic, eerie UI that feels alive.

---

## ✨ Features

### 🎭 Haunted Costume UI
- Violet / Dark-blue neon aesthetic  
- Always-on Spirit Mode  
- Animated header (pulse + glow)  
- Cinematic vignette and sweep overlay  
- Reactive particle system (particles pulse when KAISEL replies)  

### 💫 Interactive Terminal
- Type anything, and KAISEL responds  
- Replies trigger particle pulses and glow animations  
- Smooth auto-scroll and animated input caret  
- Works offline with fully local models (optional)

### 🖥 System Sidebar (Optional)
If `psutil` is installed:
- Live CPU %
- Live RAM %
- Live network usage

### 🧠 Offline AI (Optional)
If you have **Ollama** installed, KAISEL can reply using:
- LLaMA3  
- Any local model you configure

If Ollama is not installed, KAISEL still responds with atmospheric lines.

---

## 🚀 Quick Start

### 1. Clone & Install
```bash
git clone <your-repo>
cd kaisel
python -m venv venv
# Windows:
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### 2. (Optional) Enable Offline LLaMA3
Install Ollama:
https://ollama.com/

Then pull a model:
```bash
ollama pull llama3
```

---

## 📦 Packaging For Windows (Optional)

Create a standalone EXE:
```bash
pip install pyinstaller
pyinstaller --noconsole --onefile main.py
```

Executable appears under:
```
dist/KAISEL.exe
```

---

## 🎥 Demo GIF / MP4

A helper script is included:
- `record_demo.py` — captures 6 seconds of your screen at 12fps

Use FFmpeg to convert to MP4 or GIF:
```bash
ffmpeg -y -framerate 12 -i demo_frames/frame_%04d.png demo.mp4
```

---

## 📜 License
MIT License
