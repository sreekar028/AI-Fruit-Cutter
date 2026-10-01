# UI/UX Module 🎨🍉

**Module Owner:** Member 3  
**Branch:** `member3-ui`  
**Status:** ✅ Complete (v1.0.0)

---

## 1. Overview

The **UI/UX Module** provides the visual presentation layer for the **AI Fruit Cutter Game**. It transforms raw game states and computer-vision landmarks into a polished, arcade-quality user experience.

### Architecture & Data Flow

```text
       Member 1: AI Hand Tracking
                   │
                   ▼
       Member 2: Game Logic Engine
                   │ (game state, score, lives, timer, combo)
                   ▼
    ┌────────────────────────────────────────────────────────┐
    │              Member 3: UI / UX Module                  │
    │                                                        │
    │   1. UITheme (Theme & Palettes)                        │
    │      - Consistent neon gold, cyan, crimson colors      │
    │      - Vector heart icons (♥ ♥ ♥)                      │
    │      - Frosted glassmorphism panels                    │
    │                                                        │
    │   2. UI Components                                     │
    │      - ButtonPrompt (Interactive key badges)           │
    │      - ScoreCard (Score & High score)                  │
    │      - TimerWidget (Formatted MM:SS clock)             │
    │      - LivesWidget (Heart strikes)                     │
    │      - StatusBadge (Hand detection + FPS)              │
    │      - ComboNotifier (Pulsing multiplier)              │
    │                                                        │
    │   3. Screen Presenters                                 │
    │      - StartScreen (Hero banner & instructions)        │
    │      - HUDOverlay (In-game dashboard)                  │
    │      - GameOverScreen (Results modal)                  │
    │      - PauseScreen (Frosted pause menu)                │
    │                                                        │
    │   4. UIController                                      │
    │      - Master presentation orchestrator                │
    └────────────────────────────────────────────────────────┘
                   │
                   ▼
         Rendered Screen Display (OpenCV)
```

---

## 2. Directory Structure

```text
ui/
├── __init__.py           # Public API exports
├── theme.py              # Palette, typography presets, glassmorphism drawing
├── components.py         # Buttons, badges, score, hearts, timer, combo widgets
├── screens.py            # StartScreen, HUDOverlay, GameOverScreen, PauseScreen
├── ui_controller.py      # Master UI coordinator & standalone runner
└── README.md             # Documentation
```

---

## 3. Screen Layouts

### 🏠 Start / Home Screen
- **Hero Title**: `AI-BASED FRUIT CUTTER`
- **Subtitle**: `Real-Time Hand Motion Detection`
- **Instructions Card**:
  - `1. SLICE`: Move index fingertip quickly across screen
  - `2. COMBOS`: Slice multiple fruits in one swipe for bonus points
  - `3. BOMBS`: Avoid bombs (detonation costs 1 Life)
  - `4. LIVES`: Keep fruits from falling off-screen (3 strikes)
- **Primary CTA**: `[ SPACE ] START GAME` (Pulsing button)
- **Secondary CTA**: `[ Q / ESC ] QUIT`
- **Hand Status Badge**: Shows live tracking status before starting

---

### 🎮 Game Screen (In-Game HUD)
- **Score Card** (Top-Left): `SCORE: 000` & `BEST: 000`
- **Clock** (Top-Center): Stopwatch timer `MM:SS`
- **Lives** (Top-Right): Filled vector heart icons `♥ ♥ ♥`
- **Combo Banner** (Center): Pulsing multiplier `COMBO 3x! +10`
- **Status Bar** (Bottom):
  - Left: `HAND ACTIVE` (Green) / `HAND NOT DETECTED` (Red) + `FPS`
  - Right: Key hints `[ P ] Pause  |  [ R ] Restart  |  [ Q ] Quit`

---

### 💀 Game Over Screen
- **Dimmed Backdrop**: 82% obsidian overlay with crimson border
- **Title**: `GAME OVER` in high-contrast crimson
- **Results Card**:
  - `FINAL SCORE`: Large gold arcade display
  - `RECORD BADGE`: `[ NEW BEST RECORD! ]` or `Personal Best: 000`
- **Replay Buttons**:
  - `[ SPACE ] PLAY AGAIN`
  - `[ R ] Restart Round`
  - `[ Q ] Quit`

---

### ⏸️ Pause Screen
- Frosted glass modal with:
  - `[ P ] RESUME GAME`
  - `[ R ] Restart Round`
  - `[ Q ] Quit`

---

## 4. Integration with Member 1 & Member 2

The UI module sits cleanly on top of `GameEngine` without modifying internal game logic or AI algorithms:

```python
from ui import UIController

# Run standalone game with full UI:
ui = UIController()
ui.run()
```

### Preserved Keyboard Controls:
| Key | Action |
|-----|--------|
| `SPACE` | Start Game / Play Again |
| `r` / `R` | Restart Round |
| `p` / `P` | Pause / Resume |
| `q` / `Q` | Quit Application |
| `ESC` | Quit Application |

---

## 5. Standalone Testing

Run the game directly with Member 3 UI:

```bash
python -m ui.ui_controller
```
