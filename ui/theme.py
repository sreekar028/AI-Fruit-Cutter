"""
ui/theme.py
===========
UI/UX Module — Member 3
AI Fruit Cutter Game

Description:
    Design system and visual styling constants for the AI Fruit Cutter Game.
    Contains consistent color palettes (BGR format for OpenCV), typography,
    spacing, glassmorphism panel parameters, and visual style presets.
"""

import cv2
import numpy as np

# ---------------------------------------------------------------------------
# Color Palette (OpenCV uses BGR: Blue, Green, Red)
# ---------------------------------------------------------------------------
# Brand & Primary Accents
COLOR_PRIMARY_GOLD    = (0, 215, 255)     # #FFD700 Vibrant Gold
COLOR_PRIMARY_CYAN    = (255, 200, 0)     # #00C8FF Electric Cyan
COLOR_ACCENT_ORANGE   = (0, 140, 255)     # #FF8C00 Neon Orange
COLOR_ACCENT_PURPLE   = (220, 50, 150)    # Deep Violet Accent

# Status & Feedback
COLOR_SUCCESS_MINT    = (120, 230, 80)    # Soft Emerald Green (Active / Safe)
COLOR_DANGER_RED      = (40, 40, 240)     # Vibrant Crimson (Bombs / Misses / Game Over)
COLOR_WARNING_AMBER   = (0, 190, 255)     # Amber Warning
COLOR_INFO_BLUE       = (240, 160, 50)    # Sky Blue Info

# Neutrals & Glassmorphism Surfaces
COLOR_PANEL_BG        = (20, 20, 25)      # Deep Obsidian (Semi-transparent backdrop)
COLOR_CARD_BG         = (30, 30, 40)      # Elevated Dark Slate
COLOR_CARD_BORDER     = (70, 70, 90)      # Subtle Border Highlight
COLOR_BORDER_GLOW     = (180, 180, 220)   # Glow Highlight
COLOR_HEADER_BG       = (15, 15, 20)      # Header HUD Bar

# Typography Colors
COLOR_TEXT_WHITE      = (255, 255, 255)   # Crisp White
COLOR_TEXT_MUTED      = (170, 175, 185)   # Secondary Muted Slate
COLOR_TEXT_DARK       = (25, 25, 30)      # Dark text for high-contrast badges
COLOR_HEART_RED       = (50, 50, 235)     # Saturated Heart Crimson
COLOR_HEART_EMPTY     = (55, 55, 65)      # Dimmed Lost Heart

# ---------------------------------------------------------------------------
# Typography Presets
# ---------------------------------------------------------------------------
FONT_TITLE    = cv2.FONT_HERSHEY_DUPLEX
FONT_HEADING  = cv2.FONT_HERSHEY_DUPLEX
FONT_BODY     = cv2.FONT_HERSHEY_SIMPLEX
FONT_MONO     = cv2.FONT_HERSHEY_SIMPLEX

# ---------------------------------------------------------------------------
# Drawing Utilities for Glassmorphism & UI Accents
# ---------------------------------------------------------------------------
def draw_rounded_rectangle(
    frame: np.ndarray,
    top_left: tuple,
    bottom_right: tuple,
    color: tuple,
    thickness: int = 1,
    radius: int = 10,
):
    """Draw a smooth rounded rectangle on an OpenCV frame."""
    x1, y1 = top_left
    x2, y2 = bottom_right
    r = min(radius, (x2 - x1) // 2, (y2 - y1) // 2)

    if thickness == -1:
        # Filled rounded rectangle
        cv2.rectangle(frame, (x1 + r, y1), (x2 - r, y2), color, -1)
        cv2.rectangle(frame, (x1, y1 + r), (x2, y2 - r), color, -1)
        cv2.circle(frame, (x1 + r, y1 + r), r, color, -1)
        cv2.circle(frame, (x2 - r, y1 + r), r, color, -1)
        cv2.circle(frame, (x1 + r, y2 - r), r, color, -1)
        cv2.circle(frame, (x2 - r, y2 - r), r, color, -1)
    else:
        # Border rounded rectangle
        cv2.line(frame, (x1 + r, y1), (x2 - r, y1), color, thickness)
        cv2.line(frame, (x1 + r, y2), (x2 - r, y2), color, thickness)
        cv2.line(frame, (x1, y1 + r), (x1, y2 - r), color, thickness)
        cv2.line(frame, (x2, y1 + r), (x2, y2 - r), color, thickness)
        cv2.ellipse(frame, (x1 + r, y1 + r), (r, r), 180, 0, 90, color, thickness)
        cv2.ellipse(frame, (x2 - r, y1 + r), (r, r), 270, 0, 90, color, thickness)
        cv2.ellipse(frame, (x2 - r, y2 - r), (r, r), 0, 0, 90, color, thickness)
        cv2.ellipse(frame, (x1 + r, y2 - r), (r, r), 90, 0, 90, color, thickness)


def draw_glass_panel(
    frame: np.ndarray,
    top_left: tuple,
    bottom_right: tuple,
    bg_color: tuple = COLOR_PANEL_BG,
    border_color: tuple = COLOR_CARD_BORDER,
    alpha: float = 0.72,
    radius: int = 12,
):
    """
    Render a semi-transparent frosted glass panel with subtle border highlight.
    """
    x1, y1 = top_left
    x2, y2 = bottom_right
    h, w = frame.shape[:2]

    # Bounds clamp
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(w, x2), min(h, y2)
    if x2 <= x1 or y2 <= y1:
        return

    overlay = frame.copy()
    draw_rounded_rectangle(overlay, (x1, y1), (x2, y2), bg_color, thickness=-1, radius=radius)
    cv2.addWeighted(overlay, alpha, frame, 1.0 - alpha, 0, frame)

    if border_color is not None:
        draw_rounded_rectangle(frame, (x1, y1), (x2, y2), border_color, thickness=1, radius=radius)


def draw_heart_icon(frame: np.ndarray, center: tuple, size: int = 10, is_filled: bool = True):
    """
    Draw a clean, symmetric heart symbol representing player lives.
    """
    cx, cy = center
    r = size // 2
    color = COLOR_HEART_RED if is_filled else COLOR_HEART_EMPTY

    if is_filled:
        # Two top circular lobes
        cv2.circle(frame, (cx - r // 2, cy - r // 3), r // 2 + 1, color, -1)
        cv2.circle(frame, (cx + r // 2, cy - r // 3), r // 2 + 1, color, -1)
        # Inverted bottom triangle
        pts = np.array([
            [cx - r, cy - r // 4],
            [cx + r, cy - r // 4],
            [cx, cy + r],
        ], dtype=np.int32)
        cv2.fillPoly(frame, [pts], color)
        # Specular glint
        cv2.circle(frame, (cx - r // 2, cy - r // 3), max(1, r // 4), (255, 255, 255), -1)
    else:
        # Empty heart outline / dimmed strike
        cv2.circle(frame, (cx, cy), size - 1, COLOR_HEART_EMPTY, -1)
        cv2.putText(frame, "x", (cx - 4, cy + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (100, 100, 110), 1)
