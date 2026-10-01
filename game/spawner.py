"""
game/spawner.py
===============
Game Logic Module — Member 2
AI Fruit Cutter Game

Description:
    Fruit and bomb spawning system. Launches waves of fruits upwards in parabolic
    arcs with varied trajectories, velocities, fruit types, and rotation speeds.
    Includes difficulty scaling and bomb spawn probabilities.
"""

import random
import time
from typing import List
from game.fruit import Fruit, FRUIT_TYPES


class FruitSpawner:
    """
    Manages periodic fruit and bomb spawning.

    Parameters
    ----------
    bounds_width : int
        Width of the game area in pixels (default 640).
    bounds_height : int
        Height of the game area in pixels (default 480).
    base_interval : float
        Base spawn interval in seconds between waves (default 2.0s).
    bomb_chance : float
        Probability (0.0 to 1.0) of including a bomb in a wave (default 0.18).
    """

    def __init__(
        self,
        bounds_width: int = 640,
        bounds_height: int = 480,
        base_interval: float = 2.0,
        bomb_chance: float = 0.18,
    ):
        self.bounds_width = bounds_width
        self.bounds_height = bounds_height
        self.base_interval = base_interval
        self.min_interval = 1.0
        self.bomb_chance = bomb_chance

        self._last_spawn_time = 0.0
        self._current_interval = base_interval
        self._fruits_spawned_total = 0
        self._active_fruits: List[Fruit] = []

        # List of edible fruit types
        self._edible_types = [t for t in FRUIT_TYPES if t != "bomb"]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def update(self, current_time: float, current_score: int = 0) -> List[Fruit]:
        """
        Check if it's time to spawn a new wave, update active fruit physics,
        and return any newly spawned fruits.

        Parameters
        ----------
        current_time : float
            Current time in seconds (e.g., from time.time()).
        current_score : int
            Current player score (used for difficulty scaling).

        Returns
        -------
        List[Fruit]
            Newly spawned fruit instances this frame.
        """
        # Difficulty scaling: decrease spawn interval as score increases
        score_factor = min(current_score / 200.0, 1.0)
        self._current_interval = max(
            self.min_interval,
            self.base_interval - (score_factor * 0.8)
        )

        newly_spawned: List[Fruit] = []

        # Check if spawn cooldown elapsed
        if current_time - self._last_spawn_time >= self._current_interval:
            self._last_spawn_time = current_time
            newly_spawned = self._spawn_wave(current_score)
            self._active_fruits.extend(newly_spawned)

        # Update physics of all active fruits
        for fruit in self._active_fruits:
            fruit.update(self.bounds_width, self.bounds_height)

        # Clean up removed fruits
        self._active_fruits = [
            f for f in self._active_fruits
            if not (f.state == "removed" or (f.state == "missed" and f.y > self.bounds_height + 60))
        ]

        return newly_spawned

    def get_active_fruits(self) -> List[Fruit]:
        """Return list of all currently active (sliceable) fruits."""
        return [f for f in self._active_fruits if f.is_active]

    def get_all_fruits(self) -> List[Fruit]:
        """Return all fruits currently on screen (active + sliced halves)."""
        return self._active_fruits

    def reset(self):
        """Reset spawner state for a new game."""
        self._last_spawn_time = time.time()
        self._current_interval = self.base_interval
        self._fruits_spawned_total = 0
        self._active_fruits.clear()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _spawn_wave(self, current_score: int) -> List[Fruit]:
        """Generate a wave of 1 to 3 fruits launched from the bottom."""
        # Determine wave size based on score
        if current_score < 30:
            count = random.choice([1, 1, 2])
        elif current_score < 80:
            count = random.choice([1, 2, 2, 3])
        else:
            count = random.choice([2, 2, 3, 3])

        wave: List[Fruit] = []
        bomb_spawned_in_wave = False

        # Margins for launch
        margin_x = 90
        available_width = self.bounds_width - (2 * margin_x)
        slot_width = available_width / max(1, count)

        for i in range(count):
            # Slot-based X coordinate with jitter prevents overlapping launches
            slot_min = margin_x + int(i * slot_width)
            slot_max = margin_x + int((i + 1) * slot_width)
            spawn_x = random.randint(slot_min, max(slot_min + 1, slot_max))
            spawn_y = self.bounds_height + random.randint(30, 60)

            # Determine type (bomb chance applies after score >= 20, max 1 bomb per wave)
            should_spawn_bomb = (
                not bomb_spawned_in_wave
                and current_score >= 20
                and random.random() < self.bomb_chance
            )

            if should_spawn_bomb:
                f_type = "bomb"
                bomb_spawned_in_wave = True
            else:
                f_type = random.choice(self._edible_types)

            # Calculate arc velocity:
            # vy: launches high enough to reach top 25-45% of screen
            vy = random.uniform(-15.2, -18.0)

            # vx: curves gently towards the center
            center_x = self.bounds_width / 2.0
            dist_from_center = (center_x - spawn_x) / (self.bounds_width / 2.0)  # -1.0 to 1.0
            vx = dist_from_center * random.uniform(1.8, 3.8) + random.uniform(-0.5, 0.5)

            fruit = Fruit(
                fruit_type=f_type,
                x=float(spawn_x),
                y=float(spawn_y),
                vx=float(vx),
                vy=float(vy),
                gravity=0.38,
            )
            wave.append(fruit)
            self._fruits_spawned_total += 1

        return wave
