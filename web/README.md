# AI Fruit Cutter — Web Application (Browser Edition) 🍉✂️

**AI-Based Fruit Cutter Game Using Real-Time Hand Motion Detection**  
*Browser Edition powered by React, Vite, HTML5 Canvas, and Google MediaPipe Tasks Vision.*

---

## 🚀 Live Vercel Deployment Guide

This web application is completely self-contained within `web/` and deploys seamlessly on **Vercel** with zero backend servers required.

### Deploying via Vercel Dashboard:
1. Import the repository: `sreekar028/AI-Fruit-Cutter`
2. In Project Settings:
   - **Framework Preset:** Vite
   - **Root Directory:** `web`
3. Click **Deploy**.

### Deploying via Vercel CLI:
```bash
cd web
vercel
```

---

## 🛠️ Local Development & Build

### Prerequisites
- Node.js 18+ (tested on Node.js v20/v22/v26)
- npm 9+

### Setup & Run
```bash
cd web

# 1. Install dependencies
npm install

# 2. Start local development server
npm run dev
```

### Production Build
```bash
npm run build
```
Build output is generated into `web/dist/`.

---

## 🎮 How to Play

### Controls:
- **👆 Hand Slicing:** Move your **index fingertip** rapidly across the webcam feed to slice fruits in mid-air.
- **🖱️ Mouse / Touch Fallback:** Click and swipe with your mouse or drag your finger on touchscreens to slice fruits.
- **[ SPACE ]:** Start Game (from Menu) &bull; Play Again (from Game Over)
- **[ R ]:** Restart Round
- **[ P ]:** Pause / Resume
- **[ Q / ESC ]:** Quit / Exit to Start Screen

---

## 🏗️ Architecture (Mirroring Desktop Python Version)

```text
web/src/
├── ai/
│   ├── HandTracker.ts       # MediaPipe HandLandmarker WebGL/WASM (Member 1 equivalent)
│   ├── MotionDetector.ts    # Velocity, trajectory buffer, slash gestures (Member 1 equivalent)
│   └── AIController.ts      # Browser webcam getUserMedia coordinator (Member 1 equivalent)
│
├── game/
│   ├── Fruit.ts             # 6 fruit types, parabolic physics, split halves (Member 2 equivalent)
│   ├── Spawner.ts           # Wave generation, launch angles, difficulty curve (Member 2 equivalent)
│   ├── Collision.ts         # Line-segment to circle distance testing (Member 2 equivalent)
│   ├── ScoreManager.ts      # Multi-fruit combos, base scores, localStorage (Member 2 equivalent)
│   ├── LivesManager.ts      # 3 strikes, missed fruits, bomb penalties (Member 2 equivalent)
│   ├── Timer.ts             # Elapsed survival stopwatch (Member 2 equivalent)
│   ├── GameState.ts         # FSM: START, PLAYING, PAUSED, GAME_OVER (Member 2 equivalent)
│   ├── Effects.ts           # Juice particles, explosions, neon blade glow (Member 2 equivalent)
│   └── GameEngine.ts        # requestAnimationFrame central loop (Member 2 equivalent)
│
├── ui/
│   ├── theme.ts             # Palettes, typography, glassmorphism tokens (Member 3 equivalent)
│   └── components/
│       ├── HeaderHUD.tsx    # Score, High Score, Timer, Lives hearts (Member 3 equivalent)
│       ├── StartOverlay.tsx # Hero banner, how to play, Start button (Member 3 equivalent)
│       ├── GameOverModal.tsx# Final score, best score, Play Again (Member 3 equivalent)
│       ├── PauseModal.tsx   # Pause dialog (Member 3 equivalent)
│       └── StatusFooter.tsx # Hand tracking status badge, FPS counter (Member 3 equivalent)
│
├── App.tsx                  # Root component (Mirrored video + Canvas + Glassmorphism HUD)
├── App.css                  # Responsive glassmorphism stylesheet
└── main.tsx                 # DOM entry point
```

---

## 🔒 Reference Implementation Integrity
The desktop Python application (`ai/`, `game/`, `ui/`, `main.py`) remains 100% intact and untouched as the reference source of truth.
