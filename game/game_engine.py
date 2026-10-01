"""
game/game_engine.py
===================
Game Logic Module — Member 2
AI Fruit Cutter Game

Description:
    Master Game Engine coordinating all game systems:
    - Member 1 Hand Tracking input (AIController)
    - Fruit Spawning (FruitSpawner)
    - Collision Detection (CollisionDetector)
    - Score & Combo System (ScoreManager)
    - Lives & Miss Tracking (LivesManager)
    - Game Clock (GameTimer)
    - Game State Machine (GameStateManager)
    - Particle & Text VFX (EffectsManager)
    - High-performance HUD & Screen Rendering

Usage for Standalone Play:
    python -m game.game_engine

Usage for Integration with Member 3 (UI):
    from game import GameEngine
    engine = GameEngine()
    engine.start()
    while engine.is_running:
        frame, status = engine.tick()
        # use rendered frame or status dictionary
    engine.stop()
"""

import time
import cv2
import numpy as np

# Member 1 AI Module Integration
from ai.ai_controller import AIController

# Member 2 Game Logic Systems
from game.fruit import Fruit
from game.spawner import FruitSpawner
from game.collision import CollisionDetector
from game.score_manager import ScoreManager
from game.lives_manager import LivesManager
from game.timer import GameTimer
from game.game_state import GameState, GameStateManager
from game.effects import EffectsManager


class GameEngine:
    """
    Central Game Engine coordinating game logic and Member 1 hand tracking.

    Parameters
    ----------
    camera_index : int
        Webcam device index (default 0).
    width : int
        Frame width in pixels (default 640).
    height : int
        Frame height in pixels (default 480).
    countdown_duration : float, optional
        Duration in seconds for arcade mode, or None for survival mode.
    """

    def __init__(
        self,
        camera_index: int = 0,
        width: int = 640,
        height: int = 480,
        countdown_duration: float = None,
    ):
        self.width = width
        self.height = height

        # 1. Member 1 Hand Tracking Module Integration
        self.ai = AIController(
            camera_index=camera_index,
            frame_width=width,
            frame_height=height,
            mirror=True,
        )

        # 2. Game Logic Modules
        self.spawner = FruitSpawner(bounds_width=width, bounds_height=height)
        self.collision = CollisionDetector(blade_thickness=14.0)
        self.score_mgr = ScoreManager(combo_window_sec=0.5)
        self.lives_mgr = LivesManager(max_lives=3, bomb_penalty_lives=1)
        self.timer = GameTimer(countdown_duration=countdown_duration)
        self.state_mgr = GameStateManager(initial_state=GameState.START)
        self.effects = EffectsManager()

        self._running = False
        self._last_tick_time = time.time()
        self._fps = 0.0

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> bool:
        """Initialize webcam and start the engine."""
        success = self.ai.start()
        if not success:
            print("[GameEngine] Warning: Could not open webcam. Game can still run in headless mode.")
        self._running = True
        self._last_tick_time = time.time()
        return success

    def stop(self):
        """Clean up resources."""
        self._running = False
        self.ai.stop()

    @property
    def is_running(self) -> bool:
        return self._running

    def restart_game(self):
        """Reset all game systems for a fresh round."""
        self.spawner.reset()
        self.score_mgr.reset()
        self.lives_mgr.reset()
        self.timer.start()
        self.effects.reset()
        self.ai.reset_trajectory()
        self.state_mgr.restart_game()

    # ------------------------------------------------------------------
    # Main Update Loop (Decoupled Game Logic)
    # ------------------------------------------------------------------

    def update_logic(self, motion_data: dict, current_time: float) -> dict:
        """
        Pure game logic step without rendering.
        Consumes Member 1's motion data and updates all internal systems.

        Parameters
        ----------
        motion_data : dict
            Output from Member 1's AIController.
        current_time : float
            Timestamp in seconds.

        Returns
        -------
        dict
            Current frame game events (sliced fruits, misses, game over).
        """
        events = {
            "sliced_fruits": [],
            "hit_bomb": False,
            "missed_count": 0,
            "game_over": False,
        }

        if not self.state_mgr.is_playing:
            return events

        # Check countdown timer expiration
        if self.timer.is_time_up:
            self.state_mgr.trigger_game_over()
            events["game_over"] = True
            return events

        # Update combo decay
        self.score_mgr.update(current_time)

        # 1. Update Spawner & active fruit physics
        self.spawner.update(current_time, self.score_mgr.score)

        # 2. Check for Missed Fruits (fruits that fell off screen)
        for fruit in self.spawner.get_all_fruits():
            if fruit.state == "missed":
                fruit.state = "removed"
                if not fruit.is_bomb:
                    events["missed_count"] += 1
                    self.effects.spawn_floating_text("MISS!", int(fruit.x), self.height - 40, (0, 0, 255), 0.7)
                    game_over = self.lives_mgr.on_fruit_missed()
                    if game_over:
                        self.state_mgr.trigger_game_over()
                        events["game_over"] = True
                        return events

        # 3. Collision Detection with Member 1 Hand Trajectory
        active_fruits = self.spawner.get_active_fruits()
        sliced = self.collision.check_collisions(motion_data, active_fruits)

        for fruit in sliced:
            events["sliced_fruits"].append(fruit)

            if fruit.is_bomb:
                # Detonate bomb!
                events["hit_bomb"] = True
                self.effects.spawn_bomb_explosion(fruit.x, fruit.y)
                self.effects.spawn_floating_text("BOMB! -1 LIFE", int(fruit.x), int(fruit.y) - 20, (0, 0, 255), 0.8)
                game_over = self.lives_mgr.on_bomb_cut()
                self.score_mgr.register_slice(fruit, current_time)
                if game_over:
                    self.state_mgr.trigger_game_over()
                    events["game_over"] = True
                    return events
            else:
                # Sliced a delicious fruit!
                pts, combo, bonus = self.score_mgr.register_slice(fruit, current_time)
                self.effects.spawn_fruit_splash(fruit.x, fruit.y, fruit.color_splash)

                if combo >= 2:
                    self.effects.spawn_floating_text(
                        f"COMBO {combo}x! +{pts}",
                        int(fruit.x), int(fruit.y) - 20, (0, 240, 255), 0.85
                    )
                else:
                    self.effects.spawn_floating_text(
                        f"+{pts}",
                        int(fruit.x), int(fruit.y) - 20, (0, 255, 120), 0.75
                    )

        # 4. Update VFX particles
        self.effects.update(0.033)

        return events

    # ------------------------------------------------------------------
    # Frame Tick & Rendering
    # ------------------------------------------------------------------

    def tick(self) -> tuple:
        """
        Capture frame, run Member 1 hand tracking, update game logic,
        and render game layer onto the frame.

        Returns
        -------
        Tuple[np.ndarray, dict]
            (rendered_frame, game_status)
        """
        now = time.time()
        dt = max(0.001, now - self._last_tick_time)
        self._fps = 1.0 / dt
        self._last_tick_time = now

        # 1. Member 1 Hand Tracking Tick
        motion_data = self.ai.tick()
        raw_frame = self.ai.get_annotated_frame()

        if raw_frame is None:
            # Fallback if camera is disconnected: black canvas
            frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        else:
            frame = raw_frame.copy()

        # 2. Update Game Logic
        events = self.update_logic(motion_data, now)

        # 3. Render Game Visuals
        self.render(frame, motion_data)

        status = {
            "state": self.state_mgr.state.value,
            "score": self.score_mgr.score,
            "high_score": self.score_mgr.high_score,
            "lives": self.lives_mgr.lives,
            "time_str": self.timer.get_formatted_time(),
            "combo": self.score_mgr.current_combo,
            "fps": round(self._fps, 1),
            "events": events,
        }

        return frame, status

    def render(self, frame: np.ndarray, motion_data: dict):
        """Render all game visual elements onto the frame."""
        # 1. In PLAYING state, draw fruits, particles, blade, and HUD
        if self.state_mgr.is_playing:
            # Draw all fruits (active & sliced halves)
            for fruit in self.spawner.get_all_fruits():
                fruit.draw(frame)

            # Draw visual effects (juice splatters & floating texts)
            self.effects.draw(frame)

            # Draw enhanced glowing blade trail
            self.effects.draw_blade_trail(
                frame,
                motion_data.get("trajectory", []),
                motion_data.get("is_cutting", False)
            )

            # Draw HUD (Score, Lives, Timer, Combo)
            self._render_hud(frame, motion_data)

        # 2. Start Screen
        elif self.state_mgr.is_start:
            self._render_start_screen(frame, motion_data)

        # 3. Game Over Screen
        elif self.state_mgr.is_game_over:
            # Draw remaining fruits/particles in background
            for fruit in self.spawner.get_all_fruits():
                fruit.draw(frame)
            self.effects.draw(frame)
            self._render_game_over_screen(frame)

        # 4. Paused Screen
        elif self.state_mgr.is_paused:
            self._render_paused_screen(frame)

    # ------------------------------------------------------------------
    # Screen Overlays & HUD
    # ------------------------------------------------------------------

    def _render_hud(self, frame: np.ndarray, motion_data: dict):
        """Render Top HUD bar: Score, High Score, Lives, Timer, Hand Status."""
        # Semi-transparent dark header banner
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (self.width, 52), (15, 15, 15), -1)
        cv2.addWeighted(overlay, 0.65, frame, 0.35, 0, frame)

        # Score (top-left)
        cv2.putText(frame, f"SCORE: {self.score_mgr.score}", (15, 36),
                    cv2.FONT_HERSHEY_DUPLEX, 0.85, (0, 240, 255), 2)

        # High score
        cv2.putText(frame, f"BEST: {self.score_mgr.high_score}", (200, 36),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 180, 180), 1)

        # Timer (center)
        time_text = self.timer.get_formatted_time()
        cv2.putText(frame, time_text, (self.width // 2 - 35, 36),
                    cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 2)

        # Lives (top-right: represented by 3 strike boxes or crosses)
        start_x = self.width - 120
        cv2.putText(frame, "LIVES:", (start_x - 70, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

        for i in range(self.lives_mgr.max_lives):
            box_x = start_x + (i * 32)
            box_y = 16
            if i < self.lives_mgr.lives:
                # Active Life: Green heart/circle
                cv2.circle(frame, (box_x + 10, box_y + 12), 10, (0, 210, 0), -1)
                cv2.circle(frame, (box_x + 10, box_y + 12), 10, (255, 255, 255), 1)
            else:
                # Lost Life: Red X
                cv2.circle(frame, (box_x + 10, box_y + 12), 10, (40, 40, 40), -1)
                cv2.putText(frame, "X", (box_x + 4, box_y + 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 240), 2)

        # Active Combo Banner (if combo >= 2)
        if self.score_mgr.current_combo >= 2 and self.score_mgr.last_combo_text:
            text = self.score_mgr.last_combo_text
            cv2.putText(frame, text, (self.width // 2 - 110, 85),
                        cv2.FONT_HERSHEY_DUPLEX, 0.9, (0, 230, 255), 2)

        # Hand Tracking Indicator (bottom-left)
        hand_ok = motion_data.get("hand_detected", False)
        dot_color = (0, 220, 0) if hand_ok else (0, 0, 240)
        status_lbl = "Hand: ACTIVE" if hand_ok else "Hand: NOT DETECTED"
        cv2.circle(frame, (20, self.height - 20), 7, dot_color, -1)
        cv2.putText(frame, status_lbl, (35, self.height - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (220, 220, 220), 1)

    def _render_start_screen(self, frame: np.ndarray, motion_data: dict):
        """Draw start / menu screen overlay."""
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (self.width, self.height), (10, 10, 25), -1)
        cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)

        # Title
        cv2.putText(frame, "AI FRUIT CUTTER", (self.width // 2 - 210, 140),
                    cv2.FONT_HERSHEY_DUPLEX, 1.35, (0, 215, 255), 3)

        # Subtitle
        cv2.putText(frame, "Real-Time Hand Motion Detection", (self.width // 2 - 190, 185),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (240, 240, 240), 2)

        # Instructions
        cv2.putText(frame, "* Slice fruits with your Index Fingertip!", (self.width // 2 - 175, 250),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 240, 120), 2)
        cv2.putText(frame, "* Avoid Bombs - Slicing a bomb costs 1 Life!", (self.width // 2 - 175, 290),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 100, 255), 2)
        cv2.putText(frame, "* Don't let fruits fall below the screen!", (self.width // 2 - 175, 330),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (240, 200, 100), 2)

        # Action callout
        cv2.putText(frame, "Press SPACE to Start", (self.width // 2 - 150, 400),
                    cv2.FONT_HERSHEY_DUPLEX, 0.95, (0, 255, 255), 2)

        cv2.putText(frame, "Press Q or ESC to Quit", (self.width // 2 - 105, 440),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 180, 180), 1)

    def _render_game_over_screen(self, frame: np.ndarray):
        """Draw game over summary overlay."""
        overlay = frame.copy()
        cv2.rectangle(overlay, (40, 60), (self.width - 40, self.height - 60), (10, 10, 30), -1)
        cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)
        cv2.rectangle(frame, (40, 60), (self.width - 40, self.height - 60), (0, 0, 220), 3)

        # Game Over Title
        cv2.putText(frame, "GAME OVER", (self.width // 2 - 145, 135),
                    cv2.FONT_HERSHEY_DUPLEX, 1.4, (0, 50, 255), 3)

        # Stats
        cv2.putText(frame, f"Final Score   : {self.score_mgr.score}", (self.width // 2 - 130, 200),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.85, (0, 240, 255), 2)
        cv2.putText(frame, f"High Score    : {self.score_mgr.high_score}", (self.width // 2 - 130, 245),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.85, (0, 255, 120), 2)
        cv2.putText(frame, f"Fruits Sliced : {self.score_mgr.fruits_sliced_total}", (self.width // 2 - 130, 290),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.85, (220, 220, 220), 2)

        # Prompt
        cv2.putText(frame, "Press SPACE or R to Restart", (self.width // 2 - 180, 360),
                    cv2.FONT_HERSHEY_DUPLEX, 0.9, (0, 255, 255), 2)
        cv2.putText(frame, "Press Q or ESC to Quit", (self.width // 2 - 110, 395),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (180, 180, 180), 1)

    def _render_paused_screen(self, frame: np.ndarray):
        """Draw pause overlay."""
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (self.width, self.height), (15, 15, 15), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

        cv2.putText(frame, "PAUSED", (self.width // 2 - 90, self.height // 2 - 20),
                    cv2.FONT_HERSHEY_DUPLEX, 1.3, (0, 240, 255), 3)
        cv2.putText(frame, "Press P to Resume | Q to Quit", (self.width // 2 - 160, self.height // 2 + 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (220, 220, 220), 2)


# ---------------------------------------------------------------------------
# Standalone Game Runner — run: python -m game.game_engine
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    window_name = "AI Fruit Cutter — Game (Member 2)"
    engine = GameEngine()

    if not engine.start():
        print("[ERROR] Cannot initialize webcam. Please verify camera connection.")
        exit(1)

    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    print("[INFO] AI Fruit Cutter Game running.")
    print("       Press SPACE to start/restart.")
    print("       Press P to pause/resume.")
    print("       Press Q or ESC to quit.")

    while engine.is_running:
        frame, status = engine.tick()

        cv2.imshow(window_name, frame)
        key = cv2.waitKey(1) & 0xFF

        action = engine.state_mgr.handle_key(key)
        if action == "quit":
            break
        elif action in ("start", "restart"):
            engine.restart_game()

    engine.stop()
    cv2.destroyAllWindows()
    print("[INFO] Game ended. Thanks for playing!")
