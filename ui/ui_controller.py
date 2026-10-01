"""
ui/ui_controller.py
===================
UI/UX Module — Member 3
AI Fruit Cutter Game

Description:
    Master UI Controller that manages the visual presentation layer,
    integrates with Member 1's AI hand tracking and Member 2's GameEngine,
    and renders the polished game screens and HUD overlays.

Usage:
    from ui import UIController

    ui = UIController()
    ui.run()
"""

import time
import cv2
import numpy as np

# Member 2 Game Logic Engine
from game.game_engine import GameEngine
from game.game_state import GameState

# Member 3 UI Components & Screens
from ui.screens import StartScreen, HUDOverlay, GameOverScreen, PauseScreen


class UIController:
    """
    Orchestrates the UI/UX presentation layer on top of GameEngine.

    Parameters
    ----------
    camera_index : int
        Webcam device index (default 0).
    width : int
        Canvas width in pixels (default 640).
    height : int
        Canvas height in pixels (default 480).
    window_name : str
        Name of the OpenCV display window.
    fullscreen : bool
        Whether to open the window in fullscreen mode automatically.
    """

    def __init__(
        self,
        camera_index: int = 0,
        width: int = 640,
        height: int = 480,
        window_name: str = "AI Fruit Cutter — UI/UX",
        fullscreen: bool = False,
    ):
        self.width = width
        self.height = height
        self.window_name = window_name
        self.fullscreen = fullscreen

        # Underlying Game Engine (Member 2)
        self.engine = GameEngine(
            camera_index=camera_index,
            width=width,
            height=height,
        )

        self._fps = 0.0
        self._last_time = time.time()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> bool:
        """Initialize engine and camera."""
        return self.engine.start()

    def stop(self):
        """Release camera and game resources."""
        self.engine.stop()

    @property
    def is_running(self) -> bool:
        return self.engine.is_running

    # ------------------------------------------------------------------
    # Tick & Presentation
    # ------------------------------------------------------------------

    def tick(self) -> tuple:
        """
        Advance one frame: capture webcam, run AI tracking, update game logic,
        and render Member 3's polished UI layer.

        Returns
        -------
        Tuple[np.ndarray, dict]
            (rendered_frame, game_status)
        """
        now = time.time()
        dt = max(0.001, now - self._last_time)
        self._fps = 1.0 / dt
        self._last_time = now

        # 1. Member 1 AI Tracking Tick
        motion_data = self.engine.ai.tick()
        raw_frame = self.engine.ai.get_annotated_frame()

        if raw_frame is None:
            # Fallback canvas if webcam is unavailable
            frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        else:
            frame = raw_frame.copy()

        # 2. Member 2 Game Logic Update
        events = self.engine.update_logic(motion_data, now)

        status = {
            "state": self.engine.state_mgr.state.value,
            "score": self.engine.score_mgr.score,
            "high_score": self.engine.score_mgr.high_score,
            "lives": self.engine.lives_mgr.lives,
            "time_str": self.engine.timer.get_formatted_time(),
            "combo": self.engine.score_mgr.current_combo,
            "fps": round(self._fps, 1),
            "events": events,
        }

        # 3. Member 3 UI Layer Render
        self.render(frame, status, motion_data)

        return frame, status

    def render(self, frame: np.ndarray, status: dict, motion_data: dict):
        """
        Draw Member 3's polished visual presentation layer based on game state.
        """
        state = self.engine.state_mgr.state

        # State 1: START / HOME
        if state == GameState.START:
            StartScreen.render(frame, motion_data, fps=self._fps)

        # State 2: PLAYING
        elif state == GameState.PLAYING:
            # Draw game objects (fruits & split halves)
            for fruit in self.engine.spawner.get_all_fruits():
                fruit.draw(frame)

            # Draw particles (juice splatters, bomb explosions)
            self.engine.effects.draw(frame)

            # Draw glowing blade trail
            self.engine.effects.draw_blade_trail(
                frame,
                motion_data.get("trajectory", []),
                motion_data.get("is_cutting", False),
            )

            # Render Member 3 HUD
            HUDOverlay.render(frame, status, motion_data)

        # State 3: GAME OVER
        elif state == GameState.GAME_OVER:
            # Background fruits and VFX
            for fruit in self.engine.spawner.get_all_fruits():
                fruit.draw(frame)
            self.engine.effects.draw(frame)

            # Render Game Over summary modal
            GameOverScreen.render(frame, status)

        # State 4: PAUSED
        elif state == GameState.PAUSED:
            PauseScreen.render(frame)

    # ------------------------------------------------------------------
    # Keyboard & Window Controls
    # ------------------------------------------------------------------

    def handle_key(self, key_code: int) -> str:
        """
        Delegate keyboard input to GameStateManager preserving standard keys.

        Keys:
            SPACE       -> Start / Restart
            r / R       -> Restart
            p / P       -> Pause / Resume
            q / Q / ESC -> Quit
        """
        action = self.engine.state_mgr.handle_key(key_code)
        if action in ("start", "restart"):
            self.engine.restart_game()
        return action

    def run(self):
        """Run the complete standalone interactive game loop with Member 3 UI."""
        if not self.start():
            print("[UIController] Warning: Webcam not opened, running in canvas mode.")

        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        if self.fullscreen:
            cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        print(f"[INFO] {self.window_name} started.")
        print("       SPACE : Start / Restart")
        print("       P     : Pause / Resume")
        print("       Q/ESC : Quit")

        while self.is_running:
            frame, status = self.tick()
            cv2.imshow(self.window_name, frame)

            key = cv2.waitKey(1) & 0xFF
            action = self.handle_key(key)
            if action == "quit":
                break

        self.stop()
        cv2.destroyAllWindows()
        print(f"[INFO] {self.window_name} closed.")


# ---------------------------------------------------------------------------
# Standalone Runner — run: python -m ui.ui_controller
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    controller = UIController()
    controller.run()
