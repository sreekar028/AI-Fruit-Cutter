"""
game/lives_manager.py
=====================
Game Logic Module — Member 2
AI Fruit Cutter Game

Description:
    Lives and miss tracking system. Manages player lives (default 3),
    detects missed fruits, penalizes bomb hits, and triggers Game Over
    when lives reach zero.
"""


class LivesManager:
    """
    Manages player lives, missed fruits, and bomb penalties.

    Parameters
    ----------
    max_lives : int
        Number of lives/strikes before Game Over (default 3).
    bomb_penalty_lives : int
        Number of lives deducted when a bomb is cut (default 1).
    """

    def __init__(self, max_lives: int = 3, bomb_penalty_lives: int = 1):
        self.max_lives = max_lives
        self.bomb_penalty_lives = bomb_penalty_lives

        self.lives = max_lives
        self.missed_fruits_total = 0
        self.bombs_cut_total = 0

    @property
    def is_dead(self) -> bool:
        """True if all lives have been lost."""
        return self.lives <= 0

    def on_fruit_missed(self) -> bool:
        """
        Record a fruit that fell off-screen without being sliced.

        Returns
        -------
        bool : True if this miss caused Game Over.
        """
        if self.lives > 0:
            self.lives -= 1
            self.missed_fruits_total += 1
        return self.is_dead

    def on_bomb_cut(self) -> bool:
        """
        Record a bomb collision. Penalizes player lives.

        Returns
        -------
        bool : True if this bomb hit caused Game Over.
        """
        self.lives = max(0, self.lives - self.bomb_penalty_lives)
        self.bombs_cut_total += 1
        return self.is_dead

    def reset(self):
        """Restore lives for a new game round."""
        self.lives = self.max_lives
        self.missed_fruits_total = 0
        self.bombs_cut_total = 0
