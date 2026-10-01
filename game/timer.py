"""
game/timer.py
=============
Game Logic Module — Member 2
AI Fruit Cutter Game

Description:
    Game timer system. Supports both survival timer (counts up elapsed time)
    and arcade countdown timer (counts down from duration). Handles start,
    pause, resume, and formatted display strings (MM:SS).
"""

import time


class GameTimer:
    """
    Precision game clock and stopwatch.

    Parameters
    ----------
    countdown_duration : float, optional
        If provided (e.g. 60.0), operates in countdown mode.
        If None, operates in survival mode (counting up).
    """

    def __init__(self, countdown_duration: float = None):
        self.countdown_duration = countdown_duration
        self._start_time = 0.0
        self._pause_time = 0.0
        self._total_paused_duration = 0.0
        self._is_running = False
        self._is_paused = False

    def start(self):
        """Start or restart the timer."""
        self._start_time = time.time()
        self._pause_time = 0.0
        self._total_paused_duration = 0.0
        self._is_running = True
        self._is_paused = False

    def pause(self):
        """Pause the timer."""
        if self._is_running and not self._is_paused:
            self._pause_time = time.time()
            self._is_paused = True

    def resume(self):
        """Resume from paused state."""
        if self._is_running and self._is_paused:
            self._total_paused_duration += time.time() - self._pause_time
            self._is_paused = False

    def reset(self):
        """Reset timer to initial zero state."""
        self._start_time = 0.0
        self._pause_time = 0.0
        self._total_paused_duration = 0.0
        self._is_running = False
        self._is_paused = False

    @property
    def is_running(self) -> bool:
        """True if timer is currently active."""
        return self._is_running and not self._is_paused

    @property
    def elapsed_seconds(self) -> float:
        """Total active seconds elapsed since start."""
        if not self._is_running:
            return 0.0
        if self._is_paused:
            current = self._pause_time
        else:
            current = time.time()
        return max(0.0, current - self._start_time - self._total_paused_duration)

    @property
    def remaining_seconds(self) -> float:
        """Seconds remaining if in countdown mode; returns 0 if expired or not set."""
        if self.countdown_duration is None:
            return 0.0
        return max(0.0, self.countdown_duration - self.elapsed_seconds)

    @property
    def is_time_up(self) -> bool:
        """True if countdown duration has reached 0."""
        if self.countdown_duration is None:
            return False
        return self._is_running and self.elapsed_seconds >= self.countdown_duration

    def get_formatted_time(self) -> str:
        """Return formatted time MM:SS."""
        if self.countdown_duration is not None:
            total_sec = int(self.remaining_seconds)
        else:
            total_sec = int(self.elapsed_seconds)

        minutes = total_sec // 60
        seconds = total_sec % 60
        return f"{minutes:02d}:{seconds:02d}"
