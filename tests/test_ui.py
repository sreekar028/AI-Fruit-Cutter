"""
tests/test_ui.py
================
Automated Unit & Integration Test Suite for UI/UX Module (Member 3)
AI Fruit Cutter Game

Tests:
1. Theme: drawing utilities, glass panels, vector heart icons
2. Components: ButtonPrompt, StatusBadge, ScoreCard, LivesWidget, TimerWidget, ComboNotifier
3. Screens: StartScreen, HUDOverlay, GameOverScreen, PauseScreen rendering
4. UIController: frame tick, render in all 4 states, keyboard handling
"""

import unittest
import numpy as np

from ui.theme import (
    draw_rounded_rectangle,
    draw_glass_panel,
    draw_heart_icon,
    COLOR_PRIMARY_GOLD,
    COLOR_PANEL_BG,
)
from ui.components import (
    ButtonPrompt,
    StatusBadge,
    ScoreCard,
    LivesWidget,
    TimerWidget,
    ComboNotifier,
)
from ui.screens import (
    StartScreen,
    HUDOverlay,
    GameOverScreen,
    PauseScreen,
)
from ui.ui_controller import UIController
from game.game_state import GameState


class TestUIThemeAndDrawing(unittest.TestCase):
    """Test UI theme utilities and vector drawing primitives."""

    def setUp(self):
        self.frame = np.zeros((480, 640, 3), dtype=np.uint8)

    def test_draw_rounded_rectangle(self):
        draw_rounded_rectangle(self.frame, (50, 50), (200, 150), (0, 255, 0), thickness=-1, radius=8)
        # Check that canvas was modified
        self.assertGreater(np.sum(self.frame), 0)

    def test_draw_glass_panel(self):
        draw_glass_panel(self.frame, (100, 100), (300, 250), bg_color=COLOR_PANEL_BG, alpha=0.8)
        self.assertGreater(np.sum(self.frame), 0)

    def test_draw_heart_icon(self):
        draw_heart_icon(self.frame, (150, 150), size=14, is_filled=True)
        draw_heart_icon(self.frame, (200, 150), size=14, is_filled=False)
        self.assertGreater(np.sum(self.frame), 0)


class TestUIComponents(unittest.TestCase):
    """Test individual UI components and widgets."""

    def setUp(self):
        self.frame = np.zeros((480, 640, 3), dtype=np.uint8)

    def test_button_prompt(self):
        ButtonPrompt.draw(self.frame, center=(320, 240), key_label="SPACE", action_label="START GAME")
        self.assertGreater(np.sum(self.frame), 0)

    def test_status_badge(self):
        StatusBadge.draw_hand_status(self.frame, top_left=(20, 440), is_active=True, fps=30.0)
        StatusBadge.draw_hand_status(self.frame, top_left=(20, 400), is_active=False, fps=0.0)
        self.assertGreater(np.sum(self.frame), 0)

    def test_score_card(self):
        ScoreCard.draw(self.frame, top_left=(16, 12), score=120, high_score=350)
        self.assertGreater(np.sum(self.frame), 0)

    def test_lives_widget(self):
        LivesWidget.draw(self.frame, top_right=(624, 12), current_lives=2, max_lives=3)
        self.assertGreater(np.sum(self.frame), 0)

    def test_timer_widget(self):
        TimerWidget.draw(self.frame, center_top=(320, 12), time_str="01:45")
        self.assertGreater(np.sum(self.frame), 0)

    def test_combo_notifier(self):
        ComboNotifier.draw(self.frame, center=(320, 85), combo_count=3, combo_text="COMBO 3x! +10")
        self.assertGreater(np.sum(self.frame), 0)


class TestUIScreens(unittest.TestCase):
    """Test screen presenters across all game states."""

    def setUp(self):
        self.frame = np.zeros((480, 640, 3), dtype=np.uint8)
        self.status = {
            "score": 150,
            "high_score": 200,
            "lives": 3,
            "time_str": "00:45",
            "combo": 2,
            "fps": 32.5,
        }
        self.motion = {
            "hand_detected": True,
            "finger_x": 320,
            "finger_y": 240,
            "trajectory": [(310, 240), (320, 240)],
            "is_cutting": True,
        }

    def test_start_screen_render(self):
        StartScreen.render(self.frame, self.motion, fps=30.0)
        self.assertGreater(np.sum(self.frame), 0)

    def test_hud_overlay_render(self):
        HUDOverlay.render(self.frame, self.status, self.motion)
        self.assertGreater(np.sum(self.frame), 0)

    def test_game_over_screen_render(self):
        GameOverScreen.render(self.frame, self.status)
        self.assertGreater(np.sum(self.frame), 0)

    def test_pause_screen_render(self):
        PauseScreen.render(self.frame)
        self.assertGreater(np.sum(self.frame), 0)


class TestUIController(unittest.TestCase):
    """Test master UIController lifecycle, state rendering, and input handling."""

    def test_controller_tick_and_render_all_states(self):
        controller = UIController()

        # 1. START state
        frame, status = controller.tick()
        self.assertEqual(status["state"], "START")
        self.assertIsInstance(frame, np.ndarray)

        # 2. Key SPACE -> transitions to PLAYING
        action = controller.handle_key(ord(' '))
        self.assertEqual(action, "start")
        self.assertEqual(controller.engine.state_mgr.state, GameState.PLAYING)

        frame, status = controller.tick()
        self.assertEqual(status["state"], "PLAYING")

        # 3. Key P -> PAUSED
        action = controller.handle_key(ord('p'))
        self.assertEqual(action, "pause")
        self.assertEqual(controller.engine.state_mgr.state, GameState.PAUSED)

        frame, status = controller.tick()
        self.assertEqual(status["state"], "PAUSED")

        # 4. Resume -> Trigger Game Over
        controller.handle_key(ord('p'))
        controller.engine.state_mgr.trigger_game_over()
        self.assertEqual(controller.engine.state_mgr.state, GameState.GAME_OVER)

        frame, status = controller.tick()
        self.assertEqual(status["state"], "GAME_OVER")

        # 5. Key R -> Restart
        action = controller.handle_key(ord('r'))
        self.assertEqual(action, "restart")
        self.assertEqual(controller.engine.state_mgr.state, GameState.PLAYING)


if __name__ == "__main__":
    unittest.main()
