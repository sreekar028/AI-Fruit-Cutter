"""
ui/components.py
================
UI/UX Module — Member 3
AI Fruit Cutter Game

Description:
    Reusable UI widgets and presentation components:
    - Stylized Action Buttons with key badges
    - Status Badges & Pills (Hand tracking, FPS)
    - Score & High-Score Cards
    - Hearts & Lives Widget
    - Stopwatch Timer Widget
    - Combo Multiplier Pulsing Banner
    - Cut Streak Visual Feedback
"""

import math
import time
import cv2
import numpy as np

from ui.theme import (
    COLOR_PRIMARY_GOLD,
    COLOR_PRIMARY_CYAN,
    COLOR_ACCENT_ORANGE,
    COLOR_SUCCESS_MINT,
    COLOR_DANGER_RED,
    COLOR_WARNING_AMBER,
    COLOR_TEXT_WHITE,
    COLOR_TEXT_MUTED,
    COLOR_CARD_BG,
    COLOR_CARD_BORDER,
    FONT_TITLE,
    FONT_HEADING,
    FONT_BODY,
    draw_glass_panel,
    draw_rounded_rectangle,
    draw_heart_icon,
)


class ButtonPrompt:
    """
    Renders an interactive-looking button card with a distinct keyboard shortcut badge.

    Example: [ SPACE ]  START GAME
    """

    @staticmethod
    def draw(
        frame: np.ndarray,
        center: tuple,
        key_label: str,
        action_label: str,
        width: int = 280,
        height: int = 48,
        is_primary: bool = True,
        pulse: bool = False,
    ):
        cx, cy = center
        x1 = cx - width // 2
        y1 = cy - height // 2
        x2 = cx + width // 2
        y2 = cy + height // 2

        # Pulsing scale effect for primary action
        border_color = COLOR_PRIMARY_GOLD if is_primary else COLOR_CARD_BORDER
        if pulse:
            alpha = (math.sin(time.time() * 4.5) + 1.0) / 2.0
            border_color = (
                int(COLOR_PRIMARY_GOLD[0] * alpha + 150 * (1 - alpha)),
                int(COLOR_PRIMARY_GOLD[1] * alpha + 200 * (1 - alpha)),
                int(COLOR_PRIMARY_GOLD[2] * alpha + 255 * (1 - alpha)),
            )

        # Background card
        draw_glass_panel(frame, (x1, y1), (x2, y2), bg_color=(25, 25, 35), border_color=border_color, alpha=0.85, radius=10)

        # Key badge: [ KEY ]
        badge_w = max(42, len(key_label) * 11 + 16)
        badge_x1 = x1 + 10
        badge_y1 = y1 + 8
        badge_x2 = badge_x1 + badge_w
        badge_y2 = y2 - 8
        badge_bg = (50, 50, 65) if is_primary else (40, 40, 50)
        draw_rounded_rectangle(frame, (badge_x1, badge_y1), (badge_x2, badge_y2), badge_bg, thickness=-1, radius=6)
        draw_rounded_rectangle(frame, (badge_x1, badge_y1), (badge_x2, badge_y2), border_color, thickness=1, radius=6)

        # Key text inside badge
        (tw, th), _ = cv2.getTextSize(key_label, FONT_HEADING, 0.55, 2)
        tx = badge_x1 + (badge_w - tw) // 2
        ty = badge_y1 + (badge_y2 - badge_y1 + th) // 2
        cv2.putText(frame, key_label, (tx, ty), FONT_HEADING, 0.55, COLOR_PRIMARY_GOLD if is_primary else COLOR_TEXT_WHITE, 2)

        # Action text
        at_x = badge_x2 + 14
        at_y = y1 + (height + 7) // 2
        cv2.putText(frame, action_label, (at_x, at_y), FONT_BODY, 0.62, COLOR_TEXT_WHITE, 2)


class StatusBadge:
    """Renders a sleek pill-shaped status indicator (e.g. Hand Active, FPS)."""

    @staticmethod
    def draw_hand_status(frame: np.ndarray, top_left: tuple, is_active: bool, fps: float = 0.0):
        x, y = top_left
        status_text = "HAND ACTIVE" if is_active else "HAND NOT DETECTED"
        color = COLOR_SUCCESS_MINT if is_active else COLOR_DANGER_RED

        # Pill container
        w = 230 if fps > 0 else 180
        h = 28
        draw_glass_panel(frame, (x, y), (x + w, y + h), bg_color=(20, 20, 28), border_color=(60, 60, 75), alpha=0.8, radius=8)

        # Glowing status dot
        dot_cx = x + 14
        dot_cy = y + h // 2
        cv2.circle(frame, (dot_cx, dot_cy), 5, color, -1)
        if is_active:
            # Soft radial glow
            cv2.circle(frame, (dot_cx, dot_cy), 8, color, 1)

        # Status text
        cv2.putText(frame, status_text, (x + 26, y + 19), FONT_BODY, 0.48, COLOR_TEXT_WHITE, 1)

        # FPS indicator
        if fps > 0:
            fps_str = f"{int(fps)} FPS"
            cv2.putText(frame, fps_str, (x + w - 48, y + 19), FONT_BODY, 0.42, COLOR_TEXT_MUTED, 1)


class ScoreCard:
    """Displays Score and High Score with arcade-style badges."""

    @staticmethod
    def draw(frame: np.ndarray, top_left: tuple, score: int, high_score: int):
        x, y = top_left
        w = 210
        h = 42

        draw_glass_panel(frame, (x, y), (x + w, y + h), bg_color=(20, 20, 30), border_color=(65, 65, 85), alpha=0.85, radius=8)

        # Current Score
        score_str = f"SCORE {score}"
        cv2.putText(frame, score_str, (x + 12, y + 28), FONT_HEADING, 0.72, COLOR_PRIMARY_GOLD, 2)

        # High Score badge
        best_str = f"BEST {high_score}"
        cv2.putText(frame, best_str, (x + 130, y + 27), FONT_BODY, 0.48, COLOR_TEXT_MUTED, 1)


class LivesWidget:
    """Renders 3-heart life container with heart icons (♥ ♥ ♥)."""

    @staticmethod
    def draw(frame: np.ndarray, top_right: tuple, current_lives: int, max_lives: int = 3):
        x, y = top_right
        w = 135
        h = 42
        start_x = x - w

        draw_glass_panel(frame, (start_x, y), (x, y + h), bg_color=(20, 20, 30), border_color=(65, 65, 85), alpha=0.85, radius=8)

        cv2.putText(frame, "LIVES", (start_x + 10, y + 26), FONT_BODY, 0.50, COLOR_TEXT_MUTED, 1)

        # Draw hearts
        for i in range(max_lives):
            heart_cx = start_x + 65 + (i * 22)
            heart_cy = y + 20
            is_filled = (i < current_lives)
            draw_heart_icon(frame, (heart_cx, heart_cy), size=16, is_filled=is_filled)


class TimerWidget:
    """Renders the game clock in the center of the HUD."""

    @staticmethod
    def draw(frame: np.ndarray, center_top: tuple, time_str: str):
        cx, y = center_top
        w = 110
        h = 42
        x1 = cx - w // 2
        x2 = cx + w // 2

        draw_glass_panel(frame, (x1, y), (x2, y + h), bg_color=(20, 20, 30), border_color=(65, 65, 85), alpha=0.85, radius=8)

        # Stopwatch text
        (tw, th), _ = cv2.getTextSize(time_str, FONT_HEADING, 0.75, 2)
        tx = cx - tw // 2
        ty = y + (h + th) // 2
        cv2.putText(frame, time_str, (tx, ty), FONT_HEADING, 0.75, COLOR_TEXT_WHITE, 2)


class ComboNotifier:
    """Renders dynamic pulsing combo notifications (e.g. COMBO 3x! +15)."""

    @staticmethod
    def draw(frame: np.ndarray, center: tuple, combo_count: int, combo_text: str):
        if combo_count < 2 or not combo_text:
            return

        cx, cy = center
        # Pulsing scale
        pulse = 1.0 + 0.08 * math.sin(time.time() * 10.0)
        scale = 0.85 * pulse

        (tw, th), _ = cv2.getTextSize(combo_text, FONT_HEADING, scale, 2)
        w = tw + 40
        h = th + 24
        x1 = cx - w // 2
        y1 = cy - h // 2
        x2 = cx + w // 2
        y2 = cy + h // 2

        # Glowing combo banner
        border = COLOR_PRIMARY_GOLD if combo_count >= 3 else COLOR_PRIMARY_CYAN
        draw_glass_panel(frame, (x1, y1), (x2, y2), bg_color=(25, 20, 40), border_color=border, alpha=0.9, radius=10)

        # Centered text with shadow
        tx = cx - tw // 2
        ty = cy + th // 2
        cv2.putText(frame, combo_text, (tx + 2, ty + 2), FONT_HEADING, scale, (10, 10, 20), 3)
        cv2.putText(frame, combo_text, (tx, ty), FONT_HEADING, scale, COLOR_PRIMARY_GOLD, 2)
