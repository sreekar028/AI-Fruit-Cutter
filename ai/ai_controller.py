"""
ai/ai_controller.py
===================
AI / Hand Tracking Module — Member 1
AI Fruit Cutter Game

Description:
    High-level façade that combines HandTracker + MotionDetector into a single,
    easy-to-use controller for the Game module.

    The Game module should use this class instead of calling HandTracker and
    MotionDetector directly.

Quick Integration Guide for Game Module (Member 2):
----------------------------------------------------
    from ai.ai_controller import AIController

    ai = AIController()
    ai.start()                      # opens webcam

    # Each game loop tick:
    motion = ai.get_motion_data()   # returns full motion_data dict
    frame  = ai.get_annotated_frame()  # optional: annotated BGR frame

    ai.stop()                       # releases webcam + mediapipe

Output dict (motion_data) keys:
    hand_detected      bool   — Is a hand visible this frame?
    finger_x           int    — Index fingertip X (pixels, -1 if not detected)
    finger_y           int    — Index fingertip Y (pixels, -1 if not detected)
    previous_x         int    — Fingertip X previous frame (-1 if not detected)
    previous_y         int    — Fingertip Y previous frame (-1 if not detected)
    movement_distance  float  — Distance moved since last frame (pixels)
    movement_speed     float  — Speed (pixels/ms)
    movement_direction float  — Direction angle in degrees (0=right, 90=down)
    trajectory         list   — Last N (x, y) fingertip positions
    is_cutting         bool   — True if a slash/cut gesture is detected
"""

import cv2
import numpy as np
import sys

from ai.hand_tracker   import HandTracker
from ai.motion_detector import MotionDetector


class AIController:
    """
    High-level AI controller — single entry point for the Game module.

    Parameters
    ----------
    camera_index      : int   — Webcam index (0 = default camera).
    frame_width       : int   — Requested capture width in pixels.
    frame_height      : int   — Requested capture height in pixels.
    mirror            : bool  — Flip frame horizontally (natural interaction).
    detection_conf    : float — MediaPipe detection confidence threshold.
    tracking_conf     : float — MediaPipe tracking confidence threshold.
    cut_speed_px_ms   : float — Speed threshold (px/ms) for cut detection.
    cut_distance_min  : float — Minimum distance (px) per frame for cut detection.
    trajectory_len    : int   — Number of trajectory points to keep.
    """

    def __init__(
        self,
        camera_index:     int   = 0,
        frame_width:      int   = 640,
        frame_height:     int   = 480,
        mirror:           bool  = True,
        detection_conf:   float = 0.7,
        tracking_conf:    float = 0.6,
        cut_speed_px_ms:  float = 0.4,
        cut_distance_min: float = 25.0,
        trajectory_len:   int   = 20,
    ):
        self._camera_index  = camera_index
        self._frame_width   = frame_width
        self._frame_height  = frame_height
        self._mirror        = mirror

        self._tracker  = HandTracker(
            detection_confidence=detection_conf,
            tracking_confidence=tracking_conf,
        )
        self._detector = MotionDetector(
            trajectory_len=trajectory_len,
            cut_speed_px_ms=cut_speed_px_ms,
            cut_distance_min=cut_distance_min,
        )

        self._cap:          cv2.VideoCapture = None
        self._last_frame:   np.ndarray       = None
        self._last_motion:  dict             = self._empty_motion()
        self._running:      bool             = False

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> bool:
        """
        Open the webcam and start capturing.

        Returns
        -------
        bool : True if webcam opened successfully, False otherwise.
        """
        self._cap = cv2.VideoCapture(self._camera_index)
        if not self._cap.isOpened():
            print(f"[AIController] ERROR: Cannot open camera index {self._camera_index}.")
            return False

        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH,  self._frame_width)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._frame_height)
        self._running = True
        print(f"[AIController] Webcam started (index={self._camera_index}, "
              f"{self._frame_width}x{self._frame_height}).")
        return True

    def stop(self):
        """Release the webcam and MediaPipe resources."""
        self._running = False
        if self._cap and self._cap.isOpened():
            self._cap.release()
        self._tracker.release()
        print("[AIController] Resources released.")

    # ------------------------------------------------------------------
    # Per-frame API — call these each game loop tick
    # ------------------------------------------------------------------

    def tick(self) -> dict:
        """
        Capture one frame, run hand tracking and motion detection.

        This is the PRIMARY method the Game module should call each frame.

        Returns
        -------
        dict — motion_data (see module docstring for all keys).
               Returns hand_detected=False motion data if webcam fails.
        """
        if not self._running or self._cap is None:
            return self._empty_motion()

        ret, frame = self._cap.read()
        if not ret:
            return self._empty_motion()

        if self._mirror:
            frame = cv2.flip(frame, 1)

        t_data = self._tracker.get_tracking_data(frame)
        m_data = self._detector.update(t_data)

        # Annotate and cache for get_annotated_frame()
        annotated = self._tracker.draw_landmarks(frame.copy(), t_data)
        self._draw_trajectory(annotated, m_data["trajectory"])
        self._last_frame  = annotated
        self._last_motion = m_data

        return m_data

    def get_motion_data(self) -> dict:
        """
        Return motion data from the most recent tick().

        Useful if you want to call tick() and get_motion_data() separately.
        """
        return self._last_motion

    def get_annotated_frame(self) -> np.ndarray:
        """
        Return the most recent BGR frame with landmarks + trajectory drawn.

        Returns None if tick() has not been called yet.
        """
        return self._last_frame

    def reset_trajectory(self):
        """Reset the trajectory buffer (e.g. between game rounds)."""
        self._detector.reset()

    # ------------------------------------------------------------------
    # Utility / helpers
    # ------------------------------------------------------------------

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def frame_size(self) -> tuple:
        """Return (width, height) of the capture frames."""
        return (self._frame_width, self._frame_height)

    @staticmethod
    def _draw_trajectory(frame: np.ndarray, trajectory: list):
        """Draw colour-faded trajectory line on the frame."""
        n = len(trajectory)
        for i in range(1, n):
            alpha = int(255 * i / n)
            color = (0, alpha, 255 - alpha)   # green → orange as trail ages
            cv2.line(frame, trajectory[i - 1], trajectory[i], color, 3)

    @staticmethod
    def _empty_motion() -> dict:
        return {
            "hand_detected":      False,
            "finger_x":           -1,
            "finger_y":           -1,
            "previous_x":         -1,
            "previous_y":         -1,
            "movement_distance":  0.0,
            "movement_speed":     0.0,
            "movement_direction": 0.0,
            "trajectory":         [],
            "is_cutting":         False,
        }


# ---------------------------------------------------------------------------
# Standalone integration test — run: python -m ai.ai_controller
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    ai = AIController()
    if not ai.start():
        sys.exit(1)

    print("[INFO] AI Controller running. Press 'q' to quit.")
    while True:
        motion = ai.tick()
        frame  = ai.get_annotated_frame()

        if frame is not None:
            label = "CUTTING!" if motion["is_cutting"] else "ready"
            color = (0, 0, 255) if motion["is_cutting"] else (0, 200, 0)
            cv2.putText(frame, label, (10, 460),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)
            cv2.imshow("AI Controller — Integrated Test", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    ai.stop()
    cv2.destroyAllWindows()
