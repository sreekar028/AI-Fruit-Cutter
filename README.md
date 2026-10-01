# AI Fruit Cutter Game 🍉✂️

**AI-Based Fruit Cutter Game Using Real-Time Hand Motion Detection**

A multiplayer-developed Python game where players slice fruits using real-time hand gestures detected by a webcam — no controller needed!

---

## 🏗️ Project Structure

```
AI-Fruit-Cutter/
│
├── ai/                        # Member 1 — AI / Hand Tracking Module
│   ├── hand_tracker.py        # Core hand tracking (MediaPipe + OpenCV)
│   ├── motion_detector.py     # Cutting gesture detection
│   └── README.md              # AI module documentation
│
├── game/                      # Member 2 — Game Logic Module
│   └── ...
│
├── ui/                        # Member 3 — UI / Frontend Module
│   └── ...
│
├── assets/                    # Member 4 — Assets / Resources
│   └── ...
│
├── requirements.txt           # Python dependencies
├── main.py                    # Application entry point
├── .gitignore
└── README.md
```

---

## 👥 Team Roles

| Member   | Module                  | Branch         |
|----------|-------------------------|----------------|
| Member 1 | AI / Hand Tracking      | `member1-ai`   |
| Member 2 | Game Logic              | `member2-game` |
| Member 3 | UI / Frontend           | `member3-ui`   |
| Member 4 | Assets / Resources      | `member4-assets`|

---

## 🛠️ Technologies

- **Python 3.9+**
- **OpenCV** — webcam capture and image processing
- **MediaPipe** — real-time hand landmark detection
- **NumPy** — numerical computation for motion tracking
- **Pygame** *(planned)* — game rendering

---

## 🚀 Getting Started

### Prerequisites

```bash
pip install -r requirements.txt
```

### Run the game

```bash
python main.py
```

---

## 📋 Git Workflow

1. Always pull latest `main` before starting work.
2. Work only on your assigned branch.
3. Create a Pull Request to `main` when done.
4. The Integrator reviews and merges all PRs.

---

## 📄 License

MIT License — see `LICENSE` for details.
