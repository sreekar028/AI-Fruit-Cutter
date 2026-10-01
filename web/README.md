# AI Fruit Cutter — Web Application (Browser Edition) 🍉✂️

**AI-Based Fruit Cutter Game Using Real-Time Hand Motion Detection**  
*College Team Project — Browser Web Application for Vercel Deployment*

---

## 1. Project Description
The **AI-Based Fruit Cutter Game (Web Edition)** is a high-performance browser application that brings the desktop Python/OpenCV game into the modern web. Players slice tossed fruits in mid-air using their physical index finger in front of their webcam or via mouse/touch swipes, avoiding bombs and competing for high-score streaks.

The original Python desktop application (`ai/`, `game/`, `ui/`, `main.py`) serves as the official reference implementation and remains 100% intact and untouched.

---

## 2. Web Architecture
The web edition follows a strict separation of concerns mirroring the Python architecture:

```text
Browser Webcam (navigator.mediaDevices.getUserMedia)
         │
         ▼
[AI Layer] HandTracker (MediaPipe HandLandmarker WebGL/WASM)
         │
         ▼
[AI Layer] MotionDetector (Velocity, direction, trajectory queue)
         │
         ▼
[Game Layer] GameEngine (requestAnimationFrame 60 FPS loop)
         │  ├── Fruit physics & split halves
         │  ├── Spawner (parabolic launch waves)
         │  ├── Collision (continuous segment-to-circle algorithm)
         │  ├── ScoreManager (combo multipliers)
         │  ├── LivesManager (3 strikes)
         │  └── Effects (particles & blade glow)
         ▼
[UI Layer] React & HTML5 Canvas (Glassmorphism HUD, Start, GameOver, Pause)
```

---

## 3. Technologies Used
- **Frontend Framework:** React 19
- **Build Tool:** Vite 8
- **Language:** TypeScript 6
- **Computer Vision:** Google MediaPipe Tasks Vision (`@mediapipe/tasks-vision`)
- **Rendering:** HTML5 Canvas 2D API (`requestAnimationFrame`)
- **Styling:** CSS3 Glassmorphism with hardware-accelerated animations
- **Deployment Platform:** Vercel (Static Client SPA)

---

## 4. Folder Structure
```text
web/
├── public/
│   ├── favicon.svg          # Application favicon
│   └── icons.svg            # UI vector icons
├── src/
│   ├── ai/
│   │   ├── HandTracker.ts   # MediaPipe HandLandmarker wrapper
│   │   ├── MotionDetector.ts# Velocity, trajectory buffer, slash gestures
│   │   └── AIController.ts  # Browser webcam getUserMedia coordinator
│   ├── game/
│   │   ├── Fruit.ts         # 6 fruit types, parabolic physics, split halves
│   │   ├── Spawner.ts       # Wave generation, launch angles, difficulty curve
│   │   ├── Collision.ts     # Line-segment to circle distance testing
│   │   ├── ScoreManager.ts  # Multi-fruit combos, base scores, localStorage
│   │   ├── LivesManager.ts  # 3 strikes, missed fruits, bomb penalties
│   │   ├── Timer.ts         # Elapsed survival stopwatch
│   │   ├── GameState.ts     # FSM: START, PLAYING, PAUSED, GAME_OVER
│   │   ├── Effects.ts       # Juice particles, explosions, neon blade glow
│   │   └── GameEngine.ts    # requestAnimationFrame central loop
│   ├── ui/
│   │   ├── theme.ts         # Design tokens, palettes, typography
│   │   └── components/
│   │       ├── HeaderHUD.tsx    # Score, High Score, Timer, Lives hearts
│   │       ├── StartOverlay.tsx # Hero banner, how to play, Start button
│   │       ├── GameOverModal.tsx# Final score, best score, Play Again
│   │       ├── PauseModal.tsx   # Pause dialog (Resume, Restart, Home)
│   │       └── StatusFooter.tsx # Hand tracking status badge, FPS counter
│   ├── App.tsx              # Root component uniting Video, Canvas, and HUD
│   ├── App.css              # Glassmorphism styling and responsive breakpoints
│   ├── index.css            # Base stylesheet
│   └── main.tsx             # React entry point
├── vercel.json              # Vercel deployment routing and caching config
├── package.json             # NPM dependencies & build scripts
├── tsconfig.json            # TypeScript configuration
├── vite.config.ts           # Vite bundler configuration
└── README.md                # Web documentation
```

---

## 5. Installation
Ensure you have **Node.js 18+** and **npm 9+** installed:

```bash
cd web
npm install
```

---

## 6. npm install
Installs all dependencies including `@mediapipe/tasks-vision`, `react`, `react-dom`, and build tools:
```bash
npm install
```

---

## 7. npm run dev
Launches the local Vite development server with Hot Module Replacement (HMR):
```bash
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 8. npm run build
Compiles TypeScript, bundles assets, and outputs production files into `web/dist/`:
```bash
npm run build
```

---

## 9. Camera Permission Requirements
- The browser must be served over **HTTPS** (or `localhost` during development) for `navigator.mediaDevices.getUserMedia` to function.
- When prompted by the browser, click **"Allow"** to permit camera access.
- If denied, the application displays a friendly notice and enables mouse/touch swiping so you can still play without a camera.

---

## 10. Browser Requirements
- Modern Chromium browser (Google Chrome 90+, Microsoft Edge 90+, Brave)
- Mozilla Firefox 90+
- Apple Safari 15+ (macOS & iOS)
- WebGL & WebAssembly enabled for GPU MediaPipe inference

---

## 11. How Hand Tracking Works
1. `AIController` requests the user-facing webcam video stream.
2. The `<video>` element mirrors the feed (`scaleX(-1)`) for intuitive natural interaction.
3. MediaPipe `HandLandmarker` processes each frame in WebGL/GPU mode.
4. Landmark **8** (`INDEX_FINGER_TIP`) is identified and transformed from normalized coordinates $[0, 1]$ to canvas pixel coordinates $[(1 - x) \times 640, y \times 480]$.

---

## 12. How Cutting Works
1. `MotionDetector` records the last 20 fingertip positions in a rolling queue.
2. Euclidean distance and velocity ($\text{px/ms}$) are computed each frame.
3. If movement distance $\ge 25\text{px}$ and velocity $\ge 0.40\text{px/ms}$, `isCutting` is set to `true`.
4. `CollisionDetector` tests the cutting line segment $(P_{\text{prev}} \to P_{\text{curr}})$ and recent trajectory points against fruit bounding circles.
5. If the distance to the circle is $\le r_{\text{fruit}} + 14\text{px}$, a slice is registered, dividing the fruit into two halves and spawning juice particles.

---

## 13. Game Architecture
- **Fruit Physics:** Parabolic gravity arcs ($g = 0.38$) launching fruits upward from the bottom of the screen.
- **Fruit Types:** Watermelon (10 pts), Apple (15 pts), Banana (20 pts), Orange (10 pts), Strawberry (25 pts), Bomb (detonates, -1 Life, resets combo).
- **Combos:** Slicing multiple fruits within $0.50\text{s}$ awards combo bonuses (2x: +5, 3x: +10, 4x+: +20).
- **Lives:** 3 strikes. A fruit falling below the bottom border unsliced deducts 1 life.
- **Controls:**
  - `SPACE`: Start Game / Play Again
  - `R`: Restart Round
  - `P`: Pause / Resume
  - `Q` / `ESC`: Quit to Home Screen
  - Touch / Mouse swipe fallback supported on all screens

---

## 14. Manual Vercel Deployment Instructions

> **Note:** Deployment is manual. Do not run automated deployment commands.

### Option A: Via Vercel Dashboard
1. Go to [vercel.com](https://vercel.com) and log in.
2. Click **"Add New..."** $\to$ **"Project"**.
3. Import the GitHub repository: `sreekar028/AI-Fruit-Cutter`.
4. In the **Configure Project** screen:
   - **Framework Preset:** `Vite`
   - **Root Directory:** Click "Edit" and select `web`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
   - **Install Command:** `npm install`
5. Click **"Deploy"**.
6. Once deployed, Vercel provides a secure `https://your-project.vercel.app` URL with automatic SSL (allowing camera access).

### Option B: Via Vercel CLI (Manual)
```bash
cd web
vercel
```
Follow the interactive prompts:
- Link to existing project: No
- What's your project's name: `ai-fruit-cutter-web`
- In which directory is your code located: `./`
- Want to modify settings: No (Vite defaults detected)

---

## 🔒 Reference Implementation Integrity
The desktop Python implementation (`ai/`, `game/`, `ui/`, `main.py`) remains 100% intact and untouched as the reference source of truth.
