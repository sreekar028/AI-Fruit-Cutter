"""
ui/__init__.py
==============
UI/UX Module — Member 3
AI Fruit Cutter Game

Public API surface for the UI/UX presentation layer:

    from ui import UIController          # Master UI coordinator
    from ui import StartScreen           # Home / Start Screen
    from ui import HUDOverlay            # In-game HUD
    from ui import GameOverScreen        # Results modal
    from ui import PauseScreen           # Frosted glass pause menu
"""

from ui.theme import (
    COLOR_PRIMARY_GOLD,
    COLOR_PRIMARY_CYAN,
    COLOR_ACCENT_ORANGE,
    COLOR_SUCCESS_MINT,
    COLOR_DANGER_RED,
    COLOR_TEXT_WHITE,
    COLOR_TEXT_MUTED,
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

__all__ = [
    "UIController",
    "StartScreen",
    "HUDOverlay",
    "GameOverScreen",
    "PauseScreen",
    "ButtonPrompt",
    "StatusBadge",
    "ScoreCard",
    "LivesWidget",
    "TimerWidget",
    "ComboNotifier",
]

__version__ = "1.0.0"
__author__ = "Member 3 — UI/UX"
