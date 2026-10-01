"""
game/game_state.py
==================
Game Logic Module — Member 2
AI Fruit Cutter Game

Description:
    Finite state machine managing game states:
    - START (Home / Intro screen)
    - PLAYING (Active gameplay loop)
    - PAUSED (Game temporarily paused)
    - GAME_OVER (Final score & restart screen)

    Strictly preserves Member 1's existing key bindings:
    - 'q' / 'Q' / ESC : Quit application
    - SPACE           : Start game or Restart on Game Over
    - 'r' / 'R'       : Restart round immediately
    - 'p' / 'P'       : Toggle Pause
"""

from enum import Enum


class GameState(Enum):
    START = "START"
    PLAYING = "PLAYING"
    PAUSED = "PAUSED"
    GAME_OVER = "GAME_OVER"


class GameStateManager:
    """Manages game lifecycle state transitions and keyboard navigation."""

    def __init__(self, initial_state: GameState = GameState.START):
        self.state = initial_state

    @property
    def is_start(self) -> bool:
        return self.state == GameState.START

    @property
    def is_playing(self) -> bool:
        return self.state == GameState.PLAYING

    @property
    def is_paused(self) -> bool:
        return self.state == GameState.PAUSED

    @property
    def is_game_over(self) -> bool:
        return self.state == GameState.GAME_OVER

    def start_game(self):
        """Transition from START or GAME_OVER to PLAYING."""
        self.state = GameState.PLAYING

    def trigger_game_over(self):
        """Transition from PLAYING to GAME_OVER."""
        self.state = GameState.GAME_OVER

    def restart_game(self):
        """Reset directly to PLAYING."""
        self.state = GameState.PLAYING

    def toggle_pause(self):
        """Toggle between PLAYING and PAUSED."""
        if self.state == GameState.PLAYING:
            self.state = GameState.PAUSED
        elif self.state == GameState.PAUSED:
            self.state = GameState.PLAYING

    def handle_key(self, key: int) -> str:
        """
        Map OpenCV cv2.waitKey keycode to standard game actions.

        Parameters
        ----------
        key : int
            Keycode returned by cv2.waitKey(1) & 0xFF.

        Returns
        -------
        str
            Action name: 'quit', 'start', 'restart', 'pause', or ''
        """
        if key in (ord('q'), ord('Q'), 27):  # 'q' or ESC
            return "quit"

        if key == ord(' '):  # SPACE
            if self.is_start:
                self.start_game()
                return "start"
            elif self.is_game_over:
                self.restart_game()
                return "restart"

        if key in (ord('r'), ord('R')):  # 'r'
            self.restart_game()
            return "restart"

        if key in (ord('p'), ord('P')):  # 'p'
            self.toggle_pause()
            return "pause"

        return ""
