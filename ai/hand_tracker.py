"""
ai/hand_tracker.py
==================
AI / Hand Tracking Module — Member 1
AI Fruit Cutter Game

Description:
    Provides real-time hand detection and landmark tracking using MediaPipe Hands
    and OpenCV. Tracks the index fingertip (Landmark 8) position across frames
    and exposes the full landmark set for other uses.

Technologies:
    - OpenCV  : Webcam capture and frame processing
    - MediaPipe : 21-point hand landmark detection
    - NumPy   : Numerical computation

Usage (standalone test):
    python -m ai.hand_tracker

Interface for Game Module:
    tracker = HandTracker()
    data = tracker.get_tracking_data(frame)
    # data['hand_detected']   → bool
    # data['finger_x']        → int   (index fingertip X, pixel)
    # data['finger_y']        → int   (index fingertip Y, pixel)
    # data['landmarks']       → list of (x, y) tuples for all 21 landmarks
    # data['raw_landmarks']   → mediapipe NormalizedLandmarkList (advanced use)
"""

import cv2
import mediapipe as mp
import numpy as np


# ---------------------------------------------------------------------------
# MediaPipe constants
# ---------------------------------------------------------------------------
# Hand landmark indices (MediaPipe 21-point model)
WRIST           = 0
THUMB_CMC       = 1
THUMB_MCP       = 2
THUMB_IP        = 3
THUMB_TIP       = 4   # Thumb tip
INDEX_MCP       = 5
INDEX_PIP       = 6
INDEX_DIP       = 7
INDEX_TIP       = 8   # ← PRIMARY: Index fingertip we track
MIDDLE_MCP      = 9
MIDDLE_PIP      = 10
MIDDLE_DIP      = 11
MIDDLE_TIP      = 12
RING_MCP        = 13
RING_PIP        = 14
RING_DIP        = 15
RING_TIP        = 16
PINKY_MCP       = 17
PINKY_PIP       = 18
PINKY_DIP       = 19
PINKY_TIP       = 20


class HandTracker:
    """
    Real-time hand tracker using MediaPipe Hands.

    Detects a single hand and tracks the index fingertip position each frame.
    Exposes all 21 landmarks for future use by other modules.

    Parameters
    ----------
    max_hands : int
        Maximum number of hands to detect (default 1 for game performance).
    detection_confidence : float
        Minimum confidence for initial hand detection (0.0–1.0).
    tracking_confidence : float
        Minimum confidence for landmark tracking (0.0–1.0).
    """

    def __init__(
        self,
        max_hands: int = 1,
        detection_confidence: float = 0.7,
        tracking_confidence: float = 0.6,
    ):
        self._mp_hands = mp.solutions.hands
        self._mp_draw  = mp.solutions.drawing_utils
        self._mp_styles = mp.solutions.drawing_styles

        self.hands = self._mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence,
        )

        self._frame_width: int = 640
        self._frame_height: int = 480

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_tracking_data(self, frame: np.ndarray) -> dict:
        """
        Process a single BGR frame and return hand tracking data.

        Parameters
        ----------
        frame : np.ndarray
            BGR frame from OpenCV (e.g. from cv2.VideoCapture.read()).

        Returns
        -------
        dict with keys:
            hand_detected (bool)   : True if a hand was found in this frame.
            finger_x      (int)    : Index fingertip X in pixels. -1 if not detected.
            finger_y      (int)    : Index fingertip Y in pixels. -1 if not detected.
            landmarks     (list)   : List of 21 (x_px, y_px) tuples. Empty if not detected.
            raw_landmarks          : MediaPipe NormalizedLandmarkList (or None).
        """
        self._frame_height, self._frame_width = frame.shape[:2]

        # MediaPipe works on RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_frame.flags.writeable = False          # small perf boost
        results = self.hands.process(rgb_frame)
        rgb_frame.flags.writeable = True

        if not results.multi_hand_landmarks:
            return self._empty_data()

        # Use first detected hand
        hand_landmarks = results.multi_hand_landmarks[0]

        # Convert all 21 normalised landmarks → pixel coordinates
        landmarks_px = self._to_pixel_coords(hand_landmarks)

        fx, fy = landmarks_px[INDEX_TIP]

        return {
            "hand_detected": True,
            "finger_x":      fx,
            "finger_y":      fy,
            "landmarks":     landmarks_px,
            "raw_landmarks": hand_landmarks,
        }

    def draw_landmarks(self, frame: np.ndarray, tracking_data: dict) -> np.ndarray:
        """
        Draw the hand skeleton and fingertip highlight onto the frame.

        Parameters
        ----------
        frame         : BGR frame to draw on (modified in-place and returned).
        tracking_data : Dict returned by get_tracking_data().

        Returns
        -------
        np.ndarray : Annotated BGR frame.
        """
        if not tracking_data["hand_detected"]:
            return frame

        # Draw full hand skeleton
        self._mp_draw.draw_landmarks(
            frame,
            tracking_data["raw_landmarks"],
            self._mp_hands.HAND_CONNECTIONS,
            self._mp_styles.get_default_hand_landmarks_style(),
            self._mp_styles.get_default_hand_connections_style(),
        )

        # Highlight index fingertip
        fx, fy = tracking_data["finger_x"], tracking_data["finger_y"]
        cv2.circle(frame, (fx, fy), 14, (0, 255, 0), cv2.FILLED)
        cv2.circle(frame, (fx, fy), 14, (255, 255, 255), 2)

        return frame

    def release(self):
        """Release MediaPipe resources."""
        self.hands.close()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _to_pixel_coords(self, hand_landmarks) -> list:
        """Convert MediaPipe normalised landmarks to pixel (x, y) tuples."""
        coords = []
        for lm in hand_landmarks.landmark:
            x_px = int(lm.x * self._frame_width)
            y_px = int(lm.y * self._frame_height)
            coords.append((x_px, y_px))
        return coords

    @staticmethod
    def _empty_data() -> dict:
        return {
            "hand_detected": False,
            "finger_x":      -1,
            "finger_y":      -1,
            "landmarks":     [],
            "raw_landmarks": None,
        }


# ---------------------------------------------------------------------------
# Standalone test — run: python -m ai.hand_tracker
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import sys

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Cannot open webcam. Check camera connection.")
        sys.exit(1)

    tracker = HandTracker()
    print("[INFO] Hand Tracker started. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[WARNING] Failed to read frame. Retrying...")
            continue

        frame = cv2.flip(frame, 1)           # Mirror for natural interaction
        data  = tracker.get_tracking_data(frame)
        frame = tracker.draw_landmarks(frame, data)

        status = (
            f"Hand: {'YES' if data['hand_detected'] else 'NO'} | "
            f"Fingertip: ({data['finger_x']}, {data['finger_y']})"
        )
        cv2.putText(frame, status, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        cv2.imshow("Hand Tracker — AI Module (Member 1)", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    tracker.release()
    cap.release()
    cv2.destroyAllWindows()
    print("[INFO] Hand Tracker stopped.")
