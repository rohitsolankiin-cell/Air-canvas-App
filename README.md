# Air Canvas 🎨

An interactive air drawing application with gesture-based controls and finger-based color selection.

**Creator:** tubakhxn (Enhanced with OpenCV gesture detection and color palette)

Air Canvas turns your webcam into an invisible paintbrush. Wave your hand in mid-air and watch smooth digital ink appear in real time, powered by OpenCV for computer vision and gesture detection.

## Features
- Real-time hand gesture detection using OpenCV background subtraction
- **NEW: Color Palette** - Select colors by pointing at a palette on the right side
- Gesture-controlled drawing: point to draw, make a fist to pause, show an open palm to clear
- Smooth, anti-aliased strokes and a live cursor indicator for precise control
- Event hook system for gesture and canvas lifecycle extensions
- Plugin-friendly design so new behavior can be attached without modifying core logic
- Dual-window display: augmented webcam feed plus a dedicated canvas view
- Playful features: scoring, sound effects, and emoji feedback
- Demo mode for testing without webcam access
- Graceful handling of webcam availability and keyboard interrupt exits

## Requirements
- Python 3.8 or newer
- Webcam or USB camera compatible with OpenCV
- pip for dependency management

## Installation
```bash
python -m venv .venv
.\.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Run the App

### Normal Mode (with webcam)
```bash
python main.py
```

### Demo Mode (no webcam required)
```bash
python main.py --demo
```
Demo mode tests the color palette functionality without requiring camera access.

Press `q` in the Air Canvas window to exit, `c` to clear canvas.

## Color Palette

Select colors by pointing at the palette on the right side of the screen:
- Green, Blue, Red, Cyan
- Magenta, Yellow, Orange, Purple
- Deep Pink, Deep Sky Blue, White, Black

**How to use:**
1. Point your index finger at a color in the palette
2. Make a fist to start drawing with that color
3. Open palm to clear the canvas

## Troubleshooting Webcam Issues

If you get webcam access errors:

1. **Close other camera apps** (Zoom, Teams, browser tabs)
2. **Check camera permissions** in system settings
3. **Try demo mode**: `python main.py --demo`
4. **Restart your computer**
5. **Update webcam drivers**

### Common Error: MSMF Backend Error (-1072875772)
This Windows error means the camera is in use or permissions are blocked.

**Solutions:**
- Close all camera applications
- Windows Settings → Privacy → Camera → Allow access
- Try different USB ports
- Restart computer

## Extension Hooks
Air Canvas includes a hook manager for runtime extensions. Plugins can register callbacks for events such as:
- `start` - Application startup
- `gesture` - Gesture detected
- `draw` - Drawing action performed
- `clear` - Canvas cleared
- `pause` - Drawing paused
- `palette_select` - Color selected from palette
- `exit` - Application shutdown

A sample plugin is provided in `plugins/gesture_logger.py`.

## Gesture Mapping
| Gesture | How | Action |
| --- | --- | --- |
| Draw | Make a fist (all fingers folded) | Paint continuous strokes |
| Pause | Extend index finger while folding others | Lift the digital pen |
| Clear | Open palm (all fingers extended) | Clear entire canvas |
| Color Select | Point index finger at palette | Select drawing color |

## Architecture

### Core Components
- **main.py**: Main application loop, UI, and color palette
- **gesture_detector.py**: OpenCV-based gesture detection
- **canvas.py**: Drawing surface with color support
- **hooks.py**: Event system for plugins
- **utils.py**: Image processing helpers

### Plugin System
Create plugins in the `plugins/` directory. They automatically load on startup:

```python
# plugins/my_plugin.py
from hooks import hooks

@hooks.on('draw')
def on_draw(start, end, canvas):
    print(f"Drawing from {start} to {end}")

@hooks.on('palette_select')
def on_color_select(color):
    print(f"🎨 Selected color: {color}")
```
| Clear | Display an open palm (all fingers extended) | Reset the canvas to start over |

## Tips & Troubleshooting
- Ensure good, even lighting so MediaPipe can detect landmarks reliably.
- If the wrong gesture triggers, keep your hand within the frame and slow down transitions between poses.
- Strokes follow the index finger tip; move the whole hand rather than bending only the finger for smoother curves.
- If the webcam cannot be opened, close other apps that may be using it and rerun `python main.py`.

## Folder Structure
```
air-canvas/
├── main.py              # Application entry point & UI loop
├── gesture_detector.py  # MediaPipe Hands wrapper + gesture logic
├── canvas.py            # Canvas class for persistent drawing
├── utils.py             # Helper utilities for rendering overlays
├── requirements.txt     # Runtime dependencies
└── README.md            # Project guide
```

Add your own screenshots or GIFs of the running app directly to this README to showcase results.

## Fork & Extend the Project
1. Visit the GitHub repository and click **Fork** to copy it to your account.
2. Clone your fork locally: `git clone https://github.com/<your-username>/air-canvas.git`.
3. Add the original project as an upstream remote for easy syncing:
	```bash
	git remote add upstream https://github.com/tubakhxn/air-canvas.git
	git fetch upstream
	git checkout main
	git merge upstream/main
	```
4. Create a feature branch (`git checkout -b feature/new-gesture`), implement changes, and push to your fork.
5. Open a pull request against `tubakhxn/air-canvas` to share improvements.

Issues and enhancements are welcome—keep the gestures flowing!
