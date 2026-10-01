# AI Module — Hand Tracking & Motion Detection

**Module Owner:** Member 1  
**Branch:** `member1-ai`  
**Status:** ✅ Complete (v1.0.0)

---

## Overview

This module implements **real-time AI-based hand tracking and cutting gesture detection** using the webcam. It is the sole source of player input for the AI Fruit Cutter game.

### Processing Pipeline

```
Webcam
   ↓
OpenCV (BGR frame capture + flip)
   ↓
MediaPipe Hands (21-landmark detection)
   ↓
Index Fingertip Extraction (Landmark 8)
   ↓
MotionDetector (trajectory + speed + direction)
   ↓
Cut Gesture Detection (speed + distance threshold)
   ↓
motion_data dict → Game Module
```

---

## Files

| File | Description |
|------|-------------|
| [`hand_tracker.py`](hand_tracker.py) | Core hand detection using MediaPipe. Extracts 21 landmarks and returns the index fingertip pixel coordinate. |
| [`motion_detector.py`](motion_detector.py) | Stateful motion analyser. Tracks trajectory, computes speed/direction, detects cutting gestures. |
| [`ai_controller.py`](ai_controller.py) | High-level façade. Combines HandTracker + MotionDetector. **Game module should import this.** |
| [`__init__.py`](__init__.py) | Package public API. |

---

## Technologies

| Library | Version | Purpose |
|---------|---------|---------|
| `opencv-python` | ≥ 4.8 | Webcam capture, frame processing |
| `mediapipe` | ≥ 0.10 | 21-point hand landmark detection |
| `numpy` | ≥ 1.24 | Numerical arrays, frame manipulation |

---

## MediaPipe Hand Landmarks

MediaPipe detects **21 hand landmarks** (indexed 0–20):

```
  4  ← THUMB_TIP
  8  ← INDEX_TIP   ★ Primary tracking point
 12  ← MIDDLE_TIP
 16  ← RING_TIP
 20  ← PINKY_TIP
  0  ← WRIST
```

All 21 landmarks are available in `tracking_data['landmarks']` as pixel `(x, y)` tuples. Only landmark **8** (index fingertip) is used for the blade by default.

---

## Output: `motion_data` Dictionary

Every call to `AIController.tick()` returns:

| Key | Type | Description |
|-----|------|-------------|
| `hand_detected` | `bool` | Is a hand visible this frame? |
| `finger_x` | `int` | Index fingertip X (pixels). `-1` if not detected. |
| `finger_y` | `int` | Index fingertip Y (pixels). `-1` if not detected. |
| `previous_x` | `int` | Fingertip X from previous frame. |
| `previous_y` | `int` | Fingertip Y from previous frame. |
| `movement_distance` | `float` | Pixels moved since last frame. |
| `movement_speed` | `float` | Speed in pixels/ms. |
| `movement_direction` | `float` | Direction angle in degrees (0° = right, 90° = down). |
| `trajectory` | `list[(int,int)]` | Last 20 fingertip positions. |
| `is_cutting` | `bool` | `True` if a slash gesture was detected this frame. |

---

## Integration Guide for Game Module (Member 2)

```python
from ai import AIController

# Initialise once
ai = AIController(camera_index=0, frame_width=640, frame_height=480)
ai.start()

# Each game loop tick:
motion = ai.tick()

if motion["is_cutting"]:
    blade_trajectory = motion["trajectory"]
    # → check blade_trajectory against fruit bounding boxes

blade_x = motion["finger_x"]
blade_y = motion["finger_y"]

# Optional: show the AI camera view
frame = ai.get_annotated_frame()   # BGR numpy array with landmarks drawn

# On game over / quit:
ai.stop()
```

### Coordinate System

- Origin `(0, 0)` is the **top-left** of the video frame.
- X increases to the **right**.
- Y increases **downward**.
- Default resolution: `640 × 480` px.

Coordinates can be scaled to your game canvas:

```python
scale_x = game_width  / 640
scale_y = game_height / 480
game_x  = int(motion["finger_x"] * scale_x)
game_y  = int(motion["finger_y"] * scale_y)
```

---

## Cutting Gesture Detection

A **cutting/slashing** gesture is detected when **both** conditions are met in a single frame:

| Condition | Default threshold |
|-----------|-----------------|
| `movement_speed` ≥ | **0.4 px/ms** |
| `movement_distance` ≥ | **25 px** |

Both thresholds are configurable via `AIController` constructor parameters:

```python
ai = AIController(cut_speed_px_ms=0.5, cut_distance_min=30)
```

---

## Hand-Lost Handling

- If the hand disappears from the frame, `hand_detected = False` and all positional values return `-1`.
- If the hand is absent for > **0.5 seconds**, the trajectory buffer is automatically cleared (prevents ghost trails).
- This is handled gracefully — no exceptions thrown.

---

## Standalone Testing

Each file can be run independently to test without the game module:

```bash
# Test hand detection only:
python -m ai.hand_tracker

# Test motion + gesture detection:
python -m ai.motion_detector

# Test full integrated controller:
python -m ai.ai_controller
```

Press `q` to quit each test window.

---

## Performance Notes

- Target: **≥ 20 FPS** on a standard laptop webcam.
- `max_hands=1` is set for performance (single-player game).
- `rgb_frame.flags.writeable = False` during MediaPipe inference reduces copy overhead.
- Trajectory deque uses `maxlen` to avoid unbounded memory growth.
