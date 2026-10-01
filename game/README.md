# Game Logic Module 🍉🍌🍎

**Module Owner:** Member 2  
**Branch:** `feature/game-logic`  
**Status:** ✅ Complete (v1.0.0)

---

## 1. Overview

The **Game Logic Module** is responsible for all gameplay rules, fruit physics, wave spawning, continuous collision detection, scoring, combos, lives, bombs, and game states.

It integrates directly with **Member 1's AI Hand Tracking Module** (`ai.ai_controller.AIController`), translating the player's physical index finger motions and cutting trajectories into fruit slicing events in real time.

---

## 2. Architecture & Pipeline

```text
               Member 1: AI / Hand Tracking
                            │
               AIController.tick()
                            │
               motion_data dictionary:
               - finger_x, finger_y
               - previous_x, previous_y
               - trajectory [(x, y), ...]
               - is_cutting (bool)
               - movement_direction, speed
                            ▼
        ┌───────────────────────────────────────────────┐
        │        Member 2: Game Logic Module            │
        │                                               │
        │  1. FruitSpawner                              │
        │     - Waves of parabolic fruit launches       │
        │                                               │
        │  2. Fruit Physics                             │
        │     - Gravity, velocity, rotation             │
        │     - Splitting into 2 halves upon slice      │
        │                                               │
        │  3. CollisionDetector                         │
        │     - Line-segment to circle intersection     │
        │     - Trajectory raycast sweep                │
        │                                               │
        │  4. ScoreManager & LivesManager               │
        │     - Base points & Multi-fruit Combos        │
        │     - 3-strike lives & Missed fruit detection │
        │     - Bomb detonation penalty                 │
        │                                               │
        │  5. GameTimer & GameStateManager              │
        │     - START -> PLAYING -> GAME_OVER           │
        │                                               │
        │  6. EffectsManager                            │
        │     - Juice splatter & bomb spark VFX         │
        │     - Floating score numbers & glowing blade  │
        └───────────────────────────────────────────────┘
                            │
                            ▼
           Real-Time Rendered Video Frame (OpenCV)
```

---

## 3. Files in `game/`

| File | Component | Description |
|------|-----------|-------------|
| [`fruit.py`](fruit.py) | `Fruit`, `FruitHalf`, `FRUIT_TYPES` | Fruit physics, rotation, splitting halves, bomb hazard |
| [`spawner.py`](spawner.py) | `FruitSpawner` | Periodic wave launching, parabolic trajectories, jitter, difficulty curve |
| [`collision.py`](collision.py) | `CollisionDetector` | High-precision segment-to-circle collision test on Member 1's trajectory |
| [`score_manager.py`](score_manager.py) | `ScoreManager` | Base points, multi-fruit combos, decay window, high score |
| [`lives_manager.py`](lives_manager.py) | `LivesManager` | 3 strikes, missed fruit tracking, bomb damage, game-over trigger |
| [`timer.py`](timer.py) | `GameTimer` | Survival stopwatch, countdown mode, MM:SS formatting |
| [`game_state.py`](game_state.py) | `GameStateManager`, `GameState` | START / PLAYING / PAUSED / GAME_OVER state machine |
| [`effects.py`](effects.py) | `EffectsManager`, `Particle` | Juice splatter, bomb explosions, floating score text, glowing blade |
| [`game_engine.py`](game_engine.py) | `GameEngine` | Master orchestrator connecting AIController to all game systems |
| [`__init__.py`](__init__.py) | Package init | Clean public API exports |

---

## 4. Integration with Member 1 (AI Module)

The Game Logic module consumes Member 1's public interface from `ai.ai_controller.AIController`:

```python
from ai.ai_controller import AIController

ai = AIController(camera_index=0, frame_width=640, frame_height=480, mirror=True)
ai.start()

# In game loop:
motion_data = ai.tick()
raw_frame   = ai.get_annotated_frame()
```

### Exact Member 1 Inputs Consumed:

| Key | Type | How Game Logic Uses It |
|-----|------|------------------------|
| `hand_detected` | `bool` | Toggles active gameplay cutting. Displays green/red HUD indicator. |
| `finger_x`, `finger_y` | `int` | Primary point for fingertip collision and floating text anchor. |
| `previous_x`, `previous_y` | `int` | Used to form the primary cutting line segment $(P_{prev} \to P_{curr})$. |
| `trajectory` | `list[(x,y)]` | Multi-point raycast to prevent tunneling through fruits during fast swipes. |
| `is_cutting` | `bool` | Validates that movement speed & distance meet the slicing threshold. |
| `movement_direction` | `float` | Sets the angular separation angle when a fruit splits into halves. |
| `movement_speed` | `float` | Used as secondary threshold check for high-speed cutting. |

---

## 5. Fruit Types & Scoring Rules

| Fruit | Radius (px) | Points | Characteristics |
|-------|-------------|--------|-----------------|
| **Watermelon** | 36 | +10 | Forest green rind, red interior, black seeds |
| **Apple** | 28 | +15 | Crimson red skin, crisp white flesh |
| **Banana** | 26 | +20 | Bright yellow, agile arc |
| **Orange** | 30 | +10 | Vibrant orange, segmented citrus interior |
| **Strawberry** | 24 | +25 | Small, fast-moving, high value |
| **Bomb** | 30 | 0 | Charcoal black with animated burning fuse spark. Deducts 1 Life! |

### Combo System:
If multiple fruits are sliced within **0.50 seconds** of each other:
- **2 Fruits:** +5 Bonus (`COMBO 2x! +5`)
- **3 Fruits:** +10 Bonus (`COMBO 3x! +10`)
- **4+ Fruits:** +20 Bonus (`SUPER COMBO 4x! +20`)

---

## 6. Collision Detection Algorithm

To prevent "teleporting" through fruits on fast hand movements, `CollisionDetector` uses **Continuous Line-Segment to Circle Distance Testing**:

For each segment from $P_1$ to $P_2$ along the player's recent trajectory:
$$\vec{v} = P_2 - P_1, \quad \vec{w} = C_{\text{fruit}} - P_1$$
$$t = \text{clamp}\left(\frac{\vec{w} \cdot \vec{v}}{\vec{v} \cdot \vec{v}}, 0.0, 1.0\right)$$
$$P_{\text{closest}} = P_1 + t \cdot \vec{v}$$
$$\text{dist} = \|C_{\text{fruit}} - P_{\text{closest}}\|$$

A hit is registered if $\text{dist} \le r_{\text{fruit}} + \text{blade\_thickness}$.

---

## 7. Controls & Navigation

Strictly follows Member 1's key conventions:

| Key | Action |
|-----|--------|
| `SPACE` | Start game (from Start Screen) / Restart (from Game Over) |
| `r` / `R` | Restart round immediately |
| `p` / `P` | Pause / Resume gameplay |
| `q` / `Q` | Quit game |
| `ESC` | Quit game |

---

## 8. Integration Guide for Member 3 (UI / Frontend)

Member 3 can run the game engine directly or embed it:

```python
from game import GameEngine

engine = GameEngine(width=640, height=480)
engine.start()

while engine.is_running:
    # 1. Grab rendered frame and status dictionary
    frame, status = engine.tick()

    # status dictionary contains:
    #   status["score"]      -> Current score
    #   status["high_score"] -> Best score
    #   status["lives"]      -> Remaining lives (0-3)
    #   status["time_str"]   -> Formatted time ("01:23")
    #   status["state"]      -> "START", "PLAYING", "GAME_OVER", "PAUSED"
    #   status["fps"]        -> Real-time frame rate

    # 2. Display with OpenCV or blit onto Pygame / Tkinter / Web
    cv2.imshow("Game", frame)
    key = cv2.waitKey(1) & 0xFF
    action = engine.state_mgr.handle_key(key)
    if action == "quit":
        break

engine.stop()
```

---

## 9. How to Run & Test

```bash
# Run standalone game:
python -m game.game_engine
```
