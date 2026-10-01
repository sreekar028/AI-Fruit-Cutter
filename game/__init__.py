"""
game/__init__.py
================
Game Logic Module — Member 2
AI Fruit Cutter Game

Public API surface for the Game Logic module:

    from game import GameEngine          # Recommended: all-in-one coordinator
    from game import Fruit, FRUIT_TYPES  # Fruit entities & configs
    from game import FruitSpawner        # Wave & arc trajectory spawner
    from game import CollisionDetector   # Continuous trajectory collision
    from game import ScoreManager        # Score & combo system
    from game import LivesManager        # 3-lives & missed fruit tracker
    from game import GameTimer           # Game clock & countdown timer
    from game import GameState, GameStateManager # State machine
    from game import EffectsManager      # Particles & VFX
"""

from game.fruit import Fruit, FRUIT_TYPES
from game.spawner import FruitSpawner
from game.collision import CollisionDetector
from game.score_manager import ScoreManager
from game.lives_manager import LivesManager
from game.timer import GameTimer
from game.game_state import GameState, GameStateManager
from game.effects import EffectsManager
from game.game_engine import GameEngine

__all__ = [
    "GameEngine",
    "Fruit",
    "FRUIT_TYPES",
    "FruitSpawner",
    "CollisionDetector",
    "ScoreManager",
    "LivesManager",
    "GameTimer",
    "GameState",
    "GameStateManager",
    "EffectsManager",
]

__version__ = "1.0.0"
__author__ = "Member 2 — Game Logic"
