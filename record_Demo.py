# record_demo.py
# Make sure: pip install pyscreenshot Pillow
# Run while KAISEL is visible on your screen.

import os
import time
from time import sleep
from PIL import Image
import pyscreenshot as ImageGrab

outdir = "demo_frames"
os.makedirs(outdir, exist_ok=True)

duration = 6.0  # seconds
fps = 12
frames = int(duration * fps)

print(f"[record_demo] Capturing {frames} frames...")

for i in range(frames):
    img = ImageGrab.grab()  # full screen
    img.save(os.path.join(outdir, f"frame_{i:04d}.png"))
    sleep(1.0 / fps)

print("[record_demo] Done.")
print("Convert to MP4:")
print("  ffmpeg -y -framerate 12 -i demo_frames/frame_%04d.png demo.mp4")
print("Convert to GIF:")
print("  ffmpeg -y -framerate 12 -i demo_frames/frame_%04d.png -vf 'palettegen' palette.png")
print("  ffmpeg -y -framerate 12 -i demo_frames/frame_%04d.png -i palette.png -lavfi 'paletteuse' demo.gif")
