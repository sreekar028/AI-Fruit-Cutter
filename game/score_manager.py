"""
game/score_manager.py
=====================
Game Logic Module — Member 2
AI Fruit Cutter Game

Description:
    Score and combo management system. Tracks player score, high score,
    fruits sliced count, multi-fruit combos with bonus multipliers,
    and combo decay timers.
"""

import time
from typing import Tuple
from game.fruit import Fruit


class ScoreManager:
    """
    Manages scoring, combos, and game statistics.

    Parameters
    ----------
    combo_window_sec : float
        Maximum time in seconds between slices to continue a combo (default 0.45s).
    """

    def __init__(self, combo_window_sec: float = 0.45):
        self.combo_window_sec = combo_window_sec

        self.score = 0
        self.high_score = 0
        self.fruits_sliced_total = 0
        self.combos_achieved_total = 0

        # Combo tracking
        self.current_combo = 0
        self._last_slice_time = 0.0
        self.last_combo_text = ""
        self.last_combo_display_timer = 0.0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def update(self, current_time: float):
        """Update combo decay timer."""
        if self.current_combo > 0:
            if current_time - self._last_slice_time > self.combo_window_sec:
                self.current_combo = 0

    def register_slice(self, fruit: Fruit, current_time: float) -> Tuple[int, int, int]:
        """
        Record a sliced fruit and update score/combo.

        Parameters
        ----------
        fruit : Fruit
            The sliced fruit or bomb.
        current_time : float
            Timestamp of the slice.

        Returns
        -------
        Tuple[int, int, int]
            (points_awarded, combo_count, combo_bonus)
        """
        if fruit.is_bomb:
            # Cutting a bomb immediately resets combo
            self.current_combo = 0
            self.last_combo_text = ""
            return (0, 0, 0)

        # Check if slice continues an active combo
        if current_time - self._last_slice_time <= self.combo_window_sec:
            self.current_combo += 1
        else:
            self.current_combo = 1

        self._last_slice_time = current_time
        self.fruits_sliced_total += 1

        # Base fruit score
        base_points = fruit.points

        # Combo bonus
        bonus = 0
        if self.current_combo == 2:
            bonus = 5
            self.last_combo_text = "COMBO 2x! +5"
            self.combos_achieved_total += 1
        elif self.current_combo == 3:
            bonus = 10
            self.last_combo_text = "COMBO 3x! +10"
            self.combos_achieved_total += 1
        elif self.current_combo >= 4:
            bonus = 20
            self.last_combo_text = f"SUPER COMBO {self.current_combo}x! +20"
            self.combos_achieved_total += 1
        else:
            self.last_combo_text = ""

        total_awarded = base_points + bonus
        self.score += total_awarded

        if self.score > self.high_score:
            self.high_score = self.score

        return (total_awarded, self.current_combo, bonus)

    def reset(self):
        """Reset score and current combo (preserves high score)."""
        self.score = 0
        self.current_combo = 0
        self.fruits_sliced_total = 0
        self.combos_achieved_total = 0
        self._last_slice_time = 0.0
        self.last_combo_text = ""
