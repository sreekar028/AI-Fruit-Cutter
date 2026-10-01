"""
ai/__init__.py
==============
AI / Hand Tracking Module — Member 1
AI Fruit Cutter Game

Public API surface for the AI module:

    from ai import AIController          # recommended for Game module
    from ai import HandTracker           # low-level hand detection
    from ai import MotionDetector        # low-level motion analysis
"""

from ai.hand_tracker    import HandTracker
from ai.motion_detector import MotionDetector
from ai.ai_controller   import AIController

__all__ = ["AIController", "HandTracker", "MotionDetector"]
__version__ = "1.0.0"
__author__  = "Member 1 — AI/Hand Tracking"
