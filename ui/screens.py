"""
ui/screens.py
=============
UI/UX Module — Member 3
AI Fruit Cutter Game

Description:
    Screen presenters for all game states:
    - StartScreen: Hero title, instructions card, live camera preview, Start button
    - HUDOverlay: In-game dashboard with ScoreCard, TimerWidget, Lives hearts, Status badge
    - GameOverScreen: Results summary card, final score, new record badge, Play Again button
    - PauseScreen: Frosted glass pause dialog with Resume/Restart/Quit actions
"""

import cv2
import numpy as np

from ui.theme import (
    COLOR_PRIMARY_GOLD,
    COLOR_PRIMARY_CYAN,
    COLOR_ACCENT_ORANGE,
    COLOR_SUCCESS_MINT,
    COLOR_DANGER_RED,
    COLOR_TEXT_WHITE,
    COLOR_TEXT_MUTED,
    FONT_TITLE,
    FONT_HEADING,
    FONT_BODY,
    draw_glass_panel,
    draw_rounded_rectangle,
)
from ui.components import (
    ButtonPrompt,
    StatusBadge,
    ScoreCard,
    LivesWidget,
    TimerWidget,
    ComboNotifier,
)


class StartScreen:
    """Home / Start Screen with polished glassmorphism layout and instructions."""

    @staticmethod
    def render(frame: np.ndarray, motion_data: dict, fps: float = 0.0):
        h, w = frame.shape[:2]

        # 1. Dark vignette background overlay (translucent so player sees webcam)
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, h), (12, 12, 20), -1)
        cv2.addWeighted(overlay, 0.76, frame, 0.24, 0, frame)

        cx = w // 2

        # 2. Hero Title & Subtitle Banner
        title = "AI-BASED FRUIT CUTTER"
        (tw, th), _ = cv2.getTextSize(title, FONT_TITLE, 1.25, 3)
        cv2.putText(frame, title, (cx - tw // 2 + 2, 92), FONT_TITLE, 1.25, (10, 10, 20), 4)
        cv2.putText(frame, title, (cx - tw // 2, 90), FONT_TITLE, 1.25, COLOR_PRIMARY_GOLD, 3)

        sub = "Real-Time Hand Motion Detection"
        (sw, sh), _ = cv2.getTextSize(sub, FONT_HEADING, 0.65, 2)
        cv2.putText(frame, sub, (cx - sw // 2, 126), FONT_HEADING, 0.65, COLOR_TEXT_WHITE, 2)

        # 3. Instructions Glass Card
        card_w = min(540, w - 60)
        card_h = 175
        card_x1 = cx - card_w // 2
        card_y1 = 155
        card_x2 = cx + card_w // 2
        card_y2 = card_y1 + card_h

        draw_glass_panel(frame, (card_x1, card_y1), (card_x2, card_y2), bg_color=(20, 20, 32), border_color=(75, 75, 100), alpha=0.88, radius=12)

        # Header inside instructions card
        cv2.putText(frame, "HOW TO PLAY", (card_x1 + 24, card_y1 + 32), FONT_HEADING, 0.65, COLOR_PRIMARY_CYAN, 2)

        instructions = [
            ("1. SLICE", "Move your index fingertip quickly through fruits to slice them."),
            ("2. COMBOS", "Slice multiple fruits in one swift swipe for massive bonus points!"),
            ("3. BOMBS", "Avoid slicing bombs - cutting a bomb costs 1 Life!"),
            ("4. LIVES", "Do not let fruits drop below the screen (3 strikes = Game Over)."),
        ]

        for i, (label, desc) in enumerate(instructions):
            row_y = card_y1 + 62 + (i * 26)
            cv2.putText(frame, label, (card_x1 + 24, row_y), FONT_BODY, 0.48, COLOR_PRIMARY_GOLD, 2)
            cv2.putText(frame, desc, (card_x1 + 115, row_y), FONT_BODY, 0.46, COLOR_TEXT_WHITE, 1)

        # 4. Interactive Call to Action Button: [ SPACE ] START GAME
        ButtonPrompt.draw(
            frame,
            center=(cx, card_y2 + 48),
            key_label="SPACE",
            action_label="START GAME",
            width=300,
            height=50,
            is_primary=True,
            pulse=True,
        )

        # Secondary action reminder: [ Q ] QUIT
        cv2.putText(frame, "Press Q or ESC to Quit", (cx - 78, card_y2 + 95), FONT_BODY, 0.50, COLOR_TEXT_MUTED, 1)

        # 5. Hand status badge in bottom-left
        is_hand = motion_data.get("hand_detected", False)
        StatusBadge.draw_hand_status(frame, top_left=(20, h - 42), is_active=is_hand, fps=fps)


class HUDOverlay:
    """In-game HUD Dashboard Overlay."""

    @staticmethod
    def render(frame: np.ndarray, status: dict, motion_data: dict):
        h, w = frame.shape[:2]

        score = status.get("score", 0)
        high_score = status.get("high_score", 0)
        lives = status.get("lives", 3)
        time_str = status.get("time_str", "00:00")
        combo = status.get("combo", 0)
        fps = status.get("fps", 0.0)
        is_hand = motion_data.get("hand_detected", False)

        # 1. Top HUD Bar Elements
        # Score card (top-left)
        ScoreCard.draw(frame, top_left=(16, 12), score=score, high_score=high_score)

        # Timer widget (top-center)
        TimerWidget.draw(frame, center_top=(w // 2, 12), time_str=time_str)

        # Lives widget (top-right)
        LivesWidget.draw(frame, top_right=(w - 16, 12), current_lives=lives, max_lives=3)

        # 2. Active Combo Banner (if combo >= 2)
        if combo >= 2:
            combo_text = f"COMBO {combo}x!"
            if combo == 2:
                combo_text += " +5"
            elif combo == 3:
                combo_text += " +10"
            else:
                combo_text = f"SUPER COMBO {combo}x! +20"
            ComboNotifier.draw(frame, center=(w // 2, 85), combo_count=combo, combo_text=combo_text)

        # 3. Bottom Status Bar Elements
        # Hand tracking status (bottom-left)
        StatusBadge.draw_hand_status(frame, top_left=(16, h - 40), is_active=is_hand, fps=fps)

        # Navigation shortcuts reminder (bottom-right)
        hint_text = "[ P ] Pause   [ R ] Restart   [ Q ] Quit"
        (hw, _), _ = cv2.getTextSize(hint_text, FONT_BODY, 0.44, 1)
        cv2.putText(frame, hint_text, (w - hw - 20, h - 22), FONT_BODY, 0.44, (180, 185, 195), 1)


class GameOverScreen:
    """Results summary and replay card overlay."""

    @staticmethod
    def render(frame: np.ndarray, status: dict):
        h, w = frame.shape[:2]
        cx = w // 2
        cy = h // 2

        score = status.get("score", 0)
        high_score = status.get("high_score", 0)
        sliced_total = 0
        events = status.get("events", {})
        if isinstance(events, dict):
            # Check if sliced fruits are in events
            pass

        # 1. Dark frosted backdrop
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, h), (15, 10, 25), -1)
        cv2.addWeighted(overlay, 0.82, frame, 0.18, 0, frame)

        # 2. Results Modal Dialog Box
        modal_w = min(460, w - 60)
        modal_h = 320
        mx1 = cx - modal_w // 2
        my1 = cy - modal_h // 2
        mx2 = cx + modal_w // 2
        my2 = cy + modal_h // 2

        draw_glass_panel(frame, (mx1, my1), (mx2, my2), bg_color=(25, 20, 35), border_color=COLOR_DANGER_RED, alpha=0.92, radius=16)

        # Game Over Title
        title = "GAME OVER"
        (tw, th), _ = cv2.getTextSize(title, FONT_TITLE, 1.35, 3)
        cv2.putText(frame, title, (cx - tw // 2 + 2, my1 + 52), FONT_TITLE, 1.35, (10, 10, 20), 4)
        cv2.putText(frame, title, (cx - tw // 2, my1 + 50), FONT_TITLE, 1.35, COLOR_DANGER_RED, 3)

        # Score Row Card
        score_box_w = modal_w - 60
        score_box_h = 75
        sbx1 = cx - score_box_w // 2
        sby1 = my1 + 75
        draw_rounded_rectangle(frame, (sbx1, sby1), (sbx1 + score_box_w, sby1 + score_box_h), (35, 30, 48), thickness=-1, radius=10)
        draw_rounded_rectangle(frame, (sbx1, sby1), (sbx1 + score_box_w, sby1 + score_box_h), (70, 60, 90), thickness=1, radius=10)

        cv2.putText(frame, "FINAL SCORE", (cx - 65, sby1 + 25), FONT_BODY, 0.52, COLOR_TEXT_MUTED, 1)
        score_val = str(score)
        (svw, _), _ = cv2.getTextSize(score_val, FONT_HEADING, 1.15, 3)
        cv2.putText(frame, score_val, (cx - svw // 2, sby1 + 62), FONT_HEADING, 1.15, COLOR_PRIMARY_GOLD, 3)

        # Best Score comparison
        is_new_best = (score >= high_score and score > 0)
        if is_new_best:
            best_lbl = "[ NEW BEST RECORD! ]"
            (bw, _), _ = cv2.getTextSize(best_lbl, FONT_HEADING, 0.55, 2)
            cv2.putText(frame, best_lbl, (cx - bw // 2, sby1 + 105), FONT_HEADING, 0.55, COLOR_SUCCESS_MINT, 2)
        else:
            best_lbl = f"Personal Best: {high_score}"
            (bw, _), _ = cv2.getTextSize(best_lbl, FONT_BODY, 0.52, 1)
            cv2.putText(frame, best_lbl, (cx - bw // 2, sby1 + 105), FONT_BODY, 0.52, COLOR_TEXT_MUTED, 1)

        # 3. Action Buttons
        ButtonPrompt.draw(
            frame,
            center=(cx, my1 + 225),
            key_label="SPACE",
            action_label="PLAY AGAIN",
            width=280,
            height=46,
            is_primary=True,
            pulse=True,
        )

        cv2.putText(frame, "Press R to Restart  |  Press Q or ESC to Quit", (cx - 150, my2 - 20), FONT_BODY, 0.48, COLOR_TEXT_MUTED, 1)


class PauseScreen:
    """Frosted pause menu dialog."""

    @staticmethod
    def render(frame: np.ndarray):
        h, w = frame.shape[:2]
        cx = w // 2
        cy = h // 2

        # Dim backdrop
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, h), (15, 15, 20), -1)
        cv2.addWeighted(overlay, 0.70, frame, 0.30, 0, frame)

        # Dialog
        pw = 360
        ph = 200
        x1 = cx - pw // 2
        y1 = cy - ph // 2
        x2 = cx + pw // 2
        y2 = cy + ph // 2

        draw_glass_panel(frame, (x1, y1), (x2, y2), bg_color=(25, 25, 35), border_color=COLOR_PRIMARY_CYAN, alpha=0.92, radius=14)

        title = "GAME PAUSED"
        (tw, th), _ = cv2.getTextSize(title, FONT_TITLE, 1.05, 2)
        cv2.putText(frame, title, (cx - tw // 2, y1 + 45), FONT_TITLE, 1.05, COLOR_PRIMARY_CYAN, 2)

        # Action Buttons / Prompts
        ButtonPrompt.draw(
            frame,
            center=(cx, y1 + 100),
            key_label="P",
            action_label="RESUME GAME",
            width=240,
            height=40,
            is_primary=True,
            pulse=False,
        )

        cv2.putText(frame, "[ R ] Restart Round    [ Q ] Quit", (cx - 118, y2 - 24), FONT_BODY, 0.48, COLOR_TEXT_MUTED, 1)
